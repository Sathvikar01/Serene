"""Code chooses the minimum independently verifiable evidence unit (#13, #14).

The planner may bundle several requested fields into one suggestion; the policy
turns it into units it can verify one at a time, and never lets a question that
does not name its own observation reach a parent, or read as "sufficient".
"""

from __future__ import annotations

import dataclasses
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from eval.scenarios.runtime_scenarios import open_investigation
from serene.adapters.cfoai import TableCostModel
from serene.domain.events import (
    AcquisitionMode,
    EventType,
    HypothesisPrediction,
    InformationValue,
    PredictedAnswer,
)
from serene.investigation.context import ContextRetriever
from serene.investigation.minimum_data import (
    EvidenceCandidate,
    MinimumDataPolicy,
    evidence_units,
    names_field,
)
from serene.policies.acquisition import AcquisitionSafety
from serene.testing import SyntheticFamily
from tests.evidence_support import browse_reply, capture, evidence_factory
from tests.investigation_support import no_change_reply, plan_reply

ALLOWED = "example.org"


def _context() -> tuple[Any, list[str]]:
    fam = SyntheticFamily(seed="units")
    o1 = fam.observe("tearful pickup", day=0)
    o2 = fam.observe("tearful pickup again", day=1)
    pattern = fam.pattern((o1, o2), "pickups are tearful")
    inv = fam.open_investigation("why?")
    h1 = fam.hypothesis(inv, (pattern,), "The abrupt transition at pickup drives the distress")
    h2 = fam.hypothesis(inv, (pattern,), "Hunger after a long day drives the distress")
    ctx = ContextRetriever().retrieve(
        fam.state(),
        child_id=fam.child_id,
        investigation_id=inv.investigation_id,
        now=fam.clock.now(),
    )
    return ctx, [h1.hypothesis_id, h2.hypothesis_id]


CTX, (H1, H2) = _context()
SPLIT = {H1: "YES", H2: "NO"}


def _predictions(spec: dict[str, str]) -> tuple[HypothesisPrediction, ...]:
    return tuple(
        HypothesisPrediction(hypothesis_id=h, expected=PredictedAnswer(v)) for h, v in spec.items()
    )


def browse(
    cid: str,
    fields: tuple[str, ...],
    predictions: dict[str, str] = SPLIT,
    domain: str = ALLOWED,
) -> EvidenceCandidate:
    return EvidenceCandidate(
        candidate_id=cid,
        requested_fields=fields,
        acquisition_mode=AcquisitionMode.BROWSE,
        subject="daycare_pickup",
        allowed_domains=(domain,),
        rationale="r",
        predictions=_predictions(predictions),
    )


def ask(
    cid: str, fields: tuple[str, ...], question: str, predictions: dict[str, str] = SPLIT
) -> EvidenceCandidate:
    return EvidenceCandidate(
        candidate_id=cid,
        requested_fields=fields,
        acquisition_mode=AcquisitionMode.ASK_PARENT,
        question=question,
        rationale="r",
        predictions=_predictions(predictions),
    )


def policy(costs: dict[str, int] | None = None) -> MinimumDataPolicy:
    return MinimumDataPolicy(TableCostModel(costs or {}), browse_allowlist=(ALLOWED,))


def asked(*fields: str) -> Any:
    return dataclasses.replace(CTX, requested_fields_so_far=frozenset(fields))


# ---------------------------------------------------------------- units
def test_a_bundled_browse_becomes_one_unit_per_field_in_planner_order() -> None:
    bundle = browse("policy", ("pickup_window", "staff_shift_change", "room_noise"))
    units = evidence_units(bundle)
    assert [u.requested_fields for u in units] == [
        ("pickup_window",),
        ("staff_shift_change",),
        ("room_noise",),
    ]
    for unit in units:  # bounds and predictions are kept, nothing else changes
        assert unit.model_dump(exclude={"requested_fields"}) == bundle.model_dump(
            exclude={"requested_fields"}
        )


def test_a_browse_unit_repeating_a_field_is_collapsed() -> None:
    units = evidence_units(browse("dup", ("pickup_window", "pickup_window")))
    assert [u.requested_fields for u in units] == [("pickup_window",)]


def test_a_question_records_the_one_field_it_names() -> None:
    q = ask(
        "early",
        ("time_of_day", "early_pickup", "distress_present"),
        "Has she been picked up early and still cried at that pickup?",
    )
    assert [u.requested_fields for u in evidence_units(q)] == [("early_pickup",)]


def test_a_question_naming_none_of_its_fields_yields_no_unit() -> None:
    q = ask("drift", ("recovery_speed", "room_noise"), "Does she cry at other goodbyes?")
    assert evidence_units(q) == ()


@pytest.mark.parametrize(
    ("question", "field", "named"),
    [
        ("Was pickup calmer on days he had a snack just before?", "calm_after_snack", True),
        ("Does it happen at other transitions?", "other_transition", True),
        ("What colour was his jacket?", "jacket_colour", True),
        ("Is the daycare room loud?", "day_length", False),  # "day" is not "daycare"
        ("Is the room loud?", "staff_shift_change", False),
        ("Any question at all?", "___", False),  # a tag with no word names nothing
    ],
)
def test_names_field_is_a_whole_word_or_same_stem_match(
    question: str, field: str, named: bool
) -> None:
    assert names_field(question, field) is named


# ---------------------------------------------------------------- selection
def test_the_chosen_request_asks_for_exactly_one_field() -> None:
    bundle = browse("policy", ("pickup_window", "staff_shift_change", "room_noise"))
    chosen = policy().select([bundle], CTX).chosen
    assert chosen is not None and chosen.candidate.requested_fields == ("pickup_window",)


def test_each_round_moves_on_to_a_field_not_yet_asked() -> None:
    bundle = browse("policy", ("pickup_window", "staff_shift_change", "room_noise"))
    selection = policy().select([bundle], asked("pickup_window"))
    assert selection.chosen is not None
    assert selection.chosen.candidate.requested_fields == ("staff_shift_change",)
    assert ("policy[pickup_window]", "REDUNDANT_FIELDS") in selection.excluded
    done = policy().select([bundle], asked("pickup_window", "staff_shift_change", "room_noise"))
    assert done.chosen is None and done.sufficient


def test_a_misaligned_question_is_never_read_as_sufficient() -> None:
    drift = ask("drift", ("recovery_speed",), "Does she cry at other goodbyes?")
    selection = policy().select([drift, ask("low", ("snack",), "Snack?", {})], CTX)
    assert selection.chosen is None and not selection.sufficient
    assert ("drift", "QUESTION_NOT_ALIGNED") in selection.excluded
    assert policy().select([ask("low", ("snack",), "Snack?", {})], CTX).sufficient  # unchanged


def test_splitting_never_launders_an_off_allowlist_browse() -> None:
    fields = tuple(f"field_{i}" for i in range(16))
    bad = browse("tracker", fields, domain="tracker.example.net")
    selection = policy({"acquire:BROWSE": 0}).select(
        [bad, ask("safe", ("calm_after_snack",), "Calmer after a snack?")], CTX
    )
    assert selection.chosen is not None and selection.chosen.candidate.candidate_id == "safe"
    assert sum(1 for label, why in selection.excluded if why == "UNSAFE") == 16


def test_narrowing_never_launders_a_question_that_smuggles_an_intervention() -> None:
    smuggled = ask(
        "melatonin",
        ("calm_with_melatonin", "sleep_onset"),
        "Could you try giving melatonin tonight and tell me if she is calm with it?",
    )
    (unit,) = evidence_units(smuggled)
    assert policy().score(unit, CTX).safety is AcquisitionSafety.UNSAFE
    assert ("melatonin[calm_with_melatonin]", "UNSAFE") in policy().select([smuggled], CTX).excluded


def test_units_carry_no_value_their_predictions_do_not_justify() -> None:
    hidden = browse("ghost", ("pickup_window", "nap"), {"hyp_" + "0" * 32: "YES", H1: "YES"})
    for unit in evidence_units(hidden):
        assert policy().score(unit, CTX).information_value is InformationValue.MEDIUM


# ---------------------------------------------------------------- properties
FIELDS = st.sampled_from(["pickup_window", "snack_time", "room_noise", "nap", "staff_shift"])
PRED = st.dictionaries(st.sampled_from([H1, H2]), st.sampled_from(["YES", "NO"]), max_size=2)


@st.composite
def suggestion(draw: Any, cid: str) -> EvidenceCandidate:
    fields = tuple(draw(st.lists(FIELDS, min_size=1, max_size=5)))
    predictions = draw(PRED)
    if draw(st.booleans()):
        domain = draw(st.sampled_from([ALLOWED, "news.example.org", "tracker.example.net"]))
        return browse(cid, fields, predictions, domain)
    named = draw(st.lists(st.sampled_from(fields), max_size=2))
    question = "Was it " + " and ".join(f.replace("_", " ") for f in named) + "?"
    return ask(cid, fields, question, predictions)


@st.composite
def suggestions(draw: Any) -> list[EvidenceCandidate]:
    n = draw(st.integers(min_value=0, max_value=5))
    return [draw(suggestion(f"c{i}")) for i in range(n)]


@settings(max_examples=150, deadline=None)
@given(items=suggestions(), done=st.sets(FIELDS, max_size=3), order=st.randoms())
def test_selection_properties(items: list[EvidenceCandidate], done: set[str], order: Any) -> None:
    ctx = asked(*done)
    selection = policy().select(items, ctx)
    chosen = selection.chosen
    shuffled = list(items)
    order.shuffle(shuffled)
    again = policy().select(shuffled, ctx).chosen
    # Deterministic and independent of the order the planner listed things in.
    assert (chosen and chosen.candidate) == (again and again.candidate)
    if chosen is None:
        return
    unit = chosen.candidate
    (field,) = unit.requested_fields  # exactly one independently verifiable field
    source = next(c for c in items if c.candidate_id == unit.candidate_id)
    assert field in source.requested_fields and field not in done
    assert chosen.safety is AcquisitionSafety.SAFE  # safety first, whatever the cost
    assert chosen.information_value is not InformationValue.LOW
    if unit.acquisition_mode is AcquisitionMode.ASK_PARENT:
        assert names_field(unit.question or "", field)  # the parent is asked for this field


# ---------------------------------------------------------------- end to end
def _bundled_policy(hyps: list[str]) -> list[dict[str, Any]]:
    transition, hunger = hyps[0], hyps[1]
    return [
        {
            "candidate_id": "pickup-policy",
            "requested_fields": ["pickup_window", "staff_shift_change", "room_noise"],
            "acquisition_mode": "BROWSE",
            "subject": "daycare_pickup",
            "allowed_domains": ["example.org"],
            "rationale": "the page may state the pickup routine",
            "predictions": [
                {"hypothesis_id": hunger, "expected": "YES"},
                {"hypothesis_id": transition, "expected": "NO"},
            ],
        }
    ]


def test_a_bundled_suggestion_on_a_page_stating_one_field_now_verifies() -> None:
    """The page states only the pickup window. Recording the planner's bundle made the
    verifier reject the capture (REQUESTED_FIELD_UNSUPPORTED); one field verifies."""
    run = open_investigation("units-e2e", evidence=evidence_factory())
    run.rig.transport.push("plan_evidence", plan_reply(_bundled_policy))
    run.rig.transport.push("browse", browse_reply([capture()]))
    run.rig.transport.push("propose", no_change_reply())
    run.rig.transport.push("plan_evidence", plan_reply(lambda hyps: []))
    run.drive()
    events = run.rig.events()
    (request,) = [e for e in events if e.event_type is EventType.EVIDENCE_REQUESTED]
    assert tuple(request.payload["requested_fields"]) == ("pickup_window",)
    assert [e.event_type for e in events if e.event_type.value.startswith("EVIDENCE_")][-1] is (
        EventType.EVIDENCE_VERIFIED
    )
    assert not [e for e in events if e.event_type is EventType.EVIDENCE_REJECTED]


def test_a_plan_of_only_misaligned_questions_parks_instead_of_completing() -> None:
    def misaligned(hyps: list[str]) -> list[dict[str, Any]]:
        return [
            {
                "candidate_id": "drift",
                "requested_fields": ["recovery_speed"],
                "acquisition_mode": "ASK_PARENT",
                "question": "Does he cry at other goodbyes?",
                "rationale": "r",
                "predictions": [
                    {"hypothesis_id": hyps[0], "expected": "YES"},
                    {"hypothesis_id": hyps[1], "expected": "NO"},
                ],
            }
        ]

    run = open_investigation("units-park")
    run.rig.transport.push("plan_evidence", plan_reply(misaligned))
    steps = run.drive()
    assert steps[-1].to_phase is not None and steps[-1].to_phase.value == "PARKED_UNRESOLVED"
    assert steps[-1].reason_codes == ("NO_ADMISSIBLE_EVIDENCE",)
    assert not run.rig.outbox.sent  # the parent is never sent the misaligned question
