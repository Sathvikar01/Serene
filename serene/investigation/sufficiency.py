"""Evidence sufficiency: when further evidence is no longer materially useful.

The planner (a model) may suggest evidence for as long as it likes; it never decides
that an investigation is finished, and an empty plan is not evidence of anything. Code
decides, from ledger facts only:

    decisive     a request's outcome can settle its predictions: a parent's YES or NO
                 (UNSURE and silence settle nothing), or external evidence the
                 independent verifier VERIFIED (a rejected or unverified capture settles
                 nothing)
    told apart   two hypotheses are told apart once a decisive request predicted them
                 differently. Predictions are recorded with the request, before its
                 outcome, and admission keeps them to hypotheses active at that moment,
                 so nothing is credited in hindsight
    sufficient   at least one decisive request told hypotheses apart, every live
                 hypothesis was told apart from some competitor, and every pair of live
                 hypotheses was told apart

A hypothesis that enters later (a successor written while evaluating) has been told
apart from nothing yet, so it reopens the question: more evidence is useful again, or
the investigation parks when none can be had. Budget exhaustion and an empty or
inadmissible plan park; they never complete an investigation.
"""

from __future__ import annotations

from collections.abc import Collection, Iterable

from serene.domain.events import AcquisitionMode
from serene.domain.values import VerificationStatus
from serene.evidence.micro_answer import MicroAnswerValue, decode_micro_answer
from serene.policies.investigation import requests_of
from serene.projections.state import EvidenceRequestRecord, KernelState

Pair = frozenset[str]


def decisive(record: EvidenceRequestRecord, state: KernelState) -> bool:
    for evidence_id in record.evidence_ids:
        if state.verification_of(evidence_id) is not VerificationStatus.VERIFIED:
            continue
        if record.request.acquisition_mode is AcquisitionMode.BROWSE:
            return True
        answer = decode_micro_answer(state.entities[evidence_id].entity.content)
        if answer is not None and answer.answer is not MicroAnswerValue.UNSURE:
            return True
    return False


def split_by(predictions: Iterable[tuple[str, str]]) -> frozenset[Pair]:
    """Pairs of hypotheses the predictions give different answers."""
    expected = dict(predictions)
    ordered = sorted(expected)
    return frozenset(
        frozenset((a, b))
        for i, a in enumerate(ordered)
        for b in ordered[i + 1 :]
        if expected[a] != expected[b]
    )


def told_apart(investigation_id: str, state: KernelState) -> frozenset[Pair]:
    pairs: set[Pair] = set()
    for record in requests_of(investigation_id, state):
        if decisive(record, state):
            predictions = record.request.predictions
            pairs |= split_by((p.hypothesis_id, p.expected.value) for p in predictions)
    return frozenset(pairs)


def covers(live: Collection[str], pairs: Collection[Pair]) -> bool:
    """The sufficiency rule over plain values (module doc)."""
    if not live or not pairs:
        return False
    hypotheses = sorted(set(live))
    each_tested = all(any(h in pair for pair in pairs) for h in hypotheses)
    every_pair = all(
        frozenset((a, b)) in pairs for i, a in enumerate(hypotheses) for b in hypotheses[i + 1 :]
    )
    return each_tested and every_pair


def evidence_sufficient(investigation_id: str, state: KernelState, live: Collection[str]) -> bool:
    return covers(live, told_apart(investigation_id, state))
