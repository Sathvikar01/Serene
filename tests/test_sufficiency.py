"""Terminal truth is decided by code from ledger evidence, never by the planner.

The live runs of 2026-10-11 showed why COMPLETE was unreachable: EVALUATING completed
only when the planner proposed nothing admissible, and a live planner always proposes a
fresh field, so every run parked on its evidence budget whatever it had obtained. The
same rule completed an investigation with no evidence at all when a planner returned
an empty plan. `serene.investigation.sufficiency` replaces it.
"""

from __future__ import annotations

import itertools
from collections.abc import Callable
from datetime import timedelta
from typing import Any

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from eval.scenarios.runtime_scenarios import open_investigation, pickup_policy, snack_question
from serene.investigation.sufficiency import covers, split_by
from tests.evidence_support import FakeFetcher, browse_reply, evidence_factory
from tests.investigation_support import no_change_reply, plan_reply

YES, NO, UNSURE = 0, 1, 2  # Telegram answer buttons


def endless(mode: str = "ASK_PARENT", *, split: bool = True) -> Callable[[list[str]], Any]:
    """An adversarial planner: every call invents a never-seen field, forever."""
    counter = itertools.count()

    def make(hyps: list[str]) -> list[dict[str, Any]]:
        n = next(counter)
        predictions = [{"hypothesis_id": h, "expected": "YES"} for h in hyps]
        if split and len(hyps) > 1:
            predictions[-1]["expected"] = "NO"
        candidate: dict[str, Any] = {
            "candidate_id": f"invented-{n}",
            "requested_fields": [f"invented_detail_{n}"],
            "acquisition_mode": mode,
            "rationale": "one more detail could matter",
            "predictions": predictions,
        }
        if mode == "ASK_PARENT":
            candidate["question"] = f"Does invented detail {n} ever happen at pickup?"
        else:
            candidate |= {"subject": "daycare_pickup", "allowed_domains": ["example.org"]}
        return [candidate]

    return make


def phases(run: Any) -> list[Any]:
    events = run.rig.events()
    return [e.payload["to_phase"] for e in events if e.event_type.value.endswith("PHASE_CHANGED")]


def park_reasons(run: Any) -> list[str]:
    return [
        code
        for e in run.rig.events()
        if e.event_type.value == "INVESTIGATION_PHASE_CHANGED"
        and e.payload["to_phase"] == "PARKED_UNRESOLVED"
        for code in e.payload["reason_codes"]
    ]


def plan_calls(run: Any) -> int:
    return sum(1 for r in run.rig.transport.requests if r.purpose == "plan_evidence")


def asked_and_answered(seed: str, button: int, planner: Callable[..., Any]) -> Any:
    """The snack question is asked and answered; afterwards the planner is `planner`."""
    run = open_investigation(seed)
    run.rig.transport.push("plan_evidence", plan_reply(snack_question))
    run.drive()
    assert run.rig.phase(run.investigation_id) == "ASKING_HUMAN"
    assert run.script.tap_last(button).outcome == "ANSWER_RECORDED"
    for _ in range(8):
        run.rig.transport.push("propose", no_change_reply())
        run.rig.transport.push("plan_evidence", plan_reply(planner))
    return run


# ---------------------------------------------------------------- completion
def test_a_decisive_answer_completes_however_much_more_the_planner_wants() -> None:
    run = asked_and_answered("suff-decisive", NO, endless())
    calls = plan_calls(run)
    run.drive()
    assert run.rig.phase(run.investigation_id) == "COMPLETE"
    assert plan_calls(run) == calls  # decided before the planner was asked
    assert len(run.rig.outbox.sent) == 1  # no invented question reached the parent


def test_verified_discriminating_page_completes() -> None:
    run = open_investigation("suff-page", evidence=evidence_factory())
    run.rig.transport.push("plan_evidence", plan_reply(pickup_policy))
    run.rig.transport.push("browse", browse_reply())
    run.rig.transport.push("propose", no_change_reply())
    run.rig.transport.push("plan_evidence", plan_reply(endless("BROWSE")))
    run.drive()
    assert run.rig.phase(run.investigation_id) == "COMPLETE"
    assert plan_calls(run) == 1


# ---------------------------------------------------------------- no false completion
def test_an_empty_plan_never_completes_an_investigation() -> None:
    """Before: an empty plan read as 'sufficient' and completed with no evidence."""
    run = open_investigation("suff-empty")
    run.rig.transport.push("plan_evidence", plan_reply(lambda hyps: []))
    run.drive()
    assert run.rig.phase(run.investigation_id) == "PARKED_UNRESOLVED"
    assert park_reasons(run) == ["NO_ADMISSIBLE_EVIDENCE"]
    assert "COMPLETE" not in phases(run)


def test_an_empty_plan_after_an_unsure_answer_parks() -> None:
    run = asked_and_answered("suff-unsure-empty", UNSURE, lambda hyps: [])
    run.drive()
    assert run.rig.phase(run.investigation_id) == "PARKED_UNRESOLVED"
    assert park_reasons(run) == ["NO_ADMISSIBLE_EVIDENCE"]


def test_a_rejected_page_settles_nothing() -> None:
    fetcher = FakeFetcher(pages={"https://example.org/policies/pickup": "This page has moved."})
    run = open_investigation("suff-rejected", evidence=evidence_factory(fetcher))
    run.rig.transport.push("plan_evidence", plan_reply(pickup_policy))
    run.rig.transport.push("browse", browse_reply())
    run.rig.transport.push("propose", no_change_reply())
    run.rig.transport.push("plan_evidence", plan_reply(lambda hyps: []))
    run.drive()
    assert run.rig.phase(run.investigation_id) == "PARKED_UNRESOLVED"
    assert "COMPLETE" not in phases(run)


# ---------------------------------------------------------------- endless planner, honest park
def test_endless_discriminating_suggestions_with_no_decisive_answer_park_on_the_budget() -> None:
    run = asked_and_answered("suff-endless-unsure", UNSURE, endless())
    for _ in range(6):
        run.drive()
        if run.rig.phase(run.investigation_id) != "ASKING_HUMAN":
            break
        assert run.script.tap_last(UNSURE).outcome == "ANSWER_RECORDED"
    assert run.rig.phase(run.investigation_id) == "PARKED_UNRESOLVED"
    assert park_reasons(run) == ["EVIDENCE_BUDGET_EXHAUSTED"]
    assert len(run.rig.outbox.sent) == 3  # bounded by the evidence budget, not the planner


def test_endless_non_discriminating_suggestions_cannot_keep_it_open() -> None:
    run = asked_and_answered("suff-endless-low", UNSURE, endless(split=False))
    run.drive()
    # one-hypothesis tests are admissible (MEDIUM) but never tell anything apart
    for _ in range(6):
        if run.rig.phase(run.investigation_id) != "ASKING_HUMAN":
            break
        assert run.script.tap_last(YES).outcome == "ANSWER_RECORDED"
        run.drive()
    assert run.rig.phase(run.investigation_id) == "PARKED_UNRESOLVED"
    assert "COMPLETE" not in phases(run)


def test_parent_silence_still_parks() -> None:
    run = open_investigation("suff-silent")
    run.rig.transport.push("plan_evidence", plan_reply(snack_question))
    run.drive()
    run.rig.family.clock.advance(timedelta(hours=49))
    run.drive()
    assert park_reasons(run) == ["PARENT_NO_RESPONSE"]


# ---------------------------------------------------------------- the rule itself
def test_a_successor_hypothesis_reopens_the_question() -> None:
    a, b, a2 = "hyp_a", "hyp_b", "hyp_a2"
    told = split_by([(a, "YES"), (b, "NO")])
    assert covers({a, b}, told)
    assert not covers({a2, b}, told)  # written later: told apart from nothing yet
    assert covers({a}, told)  # the competitor was retired after being told apart
    assert not covers({a}, frozenset())  # a lone, untested hypothesis
    assert not covers(set(), told)


hyp_ids = st.sampled_from(["h1", "h2", "h3", "h4"])
requests = st.lists(
    st.tuples(
        st.dictionaries(hyp_ids, st.sampled_from(["YES", "NO"]), max_size=4),
        st.booleans(),  # decisive?
    ),
    max_size=6,
)


@settings(max_examples=200, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(live=st.sets(hyp_ids, max_size=4), history=requests, noise=requests)
def test_only_decisive_splits_decide_and_no_suggestion_can_flip_it(
    live: set[str], history: list[Any], noise: list[Any]
) -> None:
    def told(records: list[Any]) -> frozenset[frozenset[str]]:
        pairs: set[frozenset[str]] = set()
        for predictions, decisive in records:
            if decisive:
                pairs |= split_by(predictions.items())
        return frozenset(pairs)

    pairs = told(history)
    result = covers(live, pairs)
    # Undecided requests - any number of suggestions that were asked but settled
    # nothing - never change the verdict.
    undecided = [(p, False) for p, _ in noise]
    assert covers(live, told(history + undecided)) == result
    # Completion means every live pair really was told apart by decisive evidence.
    if result:
        assert all(frozenset((x, y)) in pairs for x in live for y in live if x != y)
        assert all(any(h in pair for pair in pairs) for h in live)
