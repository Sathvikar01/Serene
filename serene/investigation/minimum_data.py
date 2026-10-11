"""Minimum Sufficient Childhood Data + evidence acquisition priority (issues #13, #14).

Selects **at most one** missing observation, or none when the investigation is
already sufficient. The model may *suggest* candidates (requested fields, a
yes/no question or bounded browse target, and what each live hypothesis
predicts); every ranking input is then computed here, deterministically:

    information value (ordinal only)
        HIGH    live hypotheses predict *different* answers   (discriminates)
        MEDIUM  at least one live hypothesis makes a prediction (tests one)
        LOW     no live hypothesis predicts anything            (never asked)

    acquisition priority (lexicographic; earlier keys always dominate)
        1. safety            SAFE before NEEDS_REVIEW; UNSAFE is dropped, never ranked
        2. evidence need     candidates testing a hypothesis that has no verified support
        3. information value HIGH before MEDIUM
        4. burden            parent burden: BROWSE (none) before ASK_PARENT (one tap)
        5. latency           BROWSE (minutes) before ASK_PARENT (hours)
        6. cost              CostModel micro-USD; unknown sorts after known
        7. candidate_id      stable tie-break

Cost is consulted only between candidates equal on 1-5, so it can never outrank
safety, need or value. No numeric information gain is computed or emitted.
Candidates re-asking fields already requested in this investigation are
excluded, so the policy never asks the same thing twice.

Evidence units. Code, not the planner, decides how much one request asks for: the
smallest piece of evidence that can be verified on its own.

    BROWSE      one requested field per unit. The verifier needs every requested
                field stated in ONE capture excerpt, and nothing known before the
                capture shows that two fields sit in the same passage, so no fields
                are grouped. A suggestion naming several fields becomes one unit per
                field, in the planner's order; each keeps the suggestion's bounds and
                predictions, which only rank (BROWSE predictions are never scored as
                confirmed or contradicted).
    ASK_PARENT  one YES/NO answer is one unit, so it records one field: the first
                requested field the question itself names (`names_field`). A
                question that names none of its fields is not asking for its own
                observation and is excluded (QUESTION_NOT_ALIGNED).

Units are ranked like any candidate; a unit whose field was already requested is
REDUNDANT, so each round asks for one field not yet asked.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Annotated, Final, Protocol, Self, runtime_checkable

from pydantic import Field, StringConstraints, model_validator

from serene.domain.base import KernelModel, ShortText, Tag
from serene.domain.entities import Burden, Intervention, InterventionCategory
from serene.domain.events import (
    AcquisitionMode,
    HostName,
    HypothesisPrediction,
    InformationValue,
    SafetyClass,
)
from serene.investigation.context import InvestigationContext
from serene.policies.acquisition import AcquisitionSafety
from serene.policies.external_evidence import domain_allowed
from serene.policies.safety import classify_intervention
from serene.ports.cost import CostModel

POLICY_VERSION: Final = "minimum-sufficient-data/2"
CandidateId = Annotated[str, StringConstraints(pattern=r"^[a-z0-9_\-]{1,64}$")]

_VALUE_RANK: Final = {InformationValue.HIGH: 0, InformationValue.MEDIUM: 1, InformationValue.LOW: 2}
_BURDEN_RANK: Final = {AcquisitionMode.BROWSE: 0, AcquisitionMode.ASK_PARENT: 1}
_LATENCY_RANK: Final = {AcquisitionMode.BROWSE: 0, AcquisitionMode.ASK_PARENT: 1}
_WORD: Final = re.compile(r"[a-z0-9]+")
_STEM_MIN: Final = 4  # shorter tokens must match a whole word
_STEM_SLACK: Final = 3  # "calm" ~ "calmer", "transition" ~ "transitions"
_NOT_SUFFICIENCY: Final = frozenset({"QUESTION_NOT_ALIGNED"})


class EvidenceCandidate(KernelModel):
    """A *suggested* missing observation. Carries no value, safety or cost claim."""

    candidate_id: CandidateId
    requested_fields: tuple[Tag, ...] = Field(min_length=1, max_length=16)
    acquisition_mode: AcquisitionMode
    rationale: ShortText
    question: ShortText | None = None
    subject: Tag | None = None
    allowed_domains: tuple[HostName, ...] = Field(default=(), max_length=16)
    predictions: tuple[HypothesisPrediction, ...] = Field(default=(), max_length=16)

    @model_validator(mode="after")
    def _mode_fields(self) -> Self:
        if self.acquisition_mode is AcquisitionMode.ASK_PARENT:
            if self.question is None or self.allowed_domains or self.subject is not None:
                raise ValueError("ASK_PARENT needs a question and no browse bounds")
        elif not self.allowed_domains or self.subject is None or self.question is not None:
            raise ValueError("BROWSE needs a subject and allowed domains, and no question")
        return self


def _same_word(token: str, word: str) -> bool:
    if token == word:
        return True
    short, long = sorted((token, word), key=len)
    return (
        len(short) >= _STEM_MIN and long.startswith(short) and len(long) - len(short) <= _STEM_SLACK
    )


def names_field(question: str, field: str) -> bool:
    """Whether a question names a requested field: at least half of the field's word
    tokens appear in the question (a whole word, or the same stem). A lexical check
    on the system's own tag, never on scenario vocabulary; necessary, not sufficient."""
    tokens = _WORD.findall(field.casefold())
    words = _WORD.findall(question.casefold())
    hits = sum(1 for t in tokens if any(_same_word(t, w) for w in words))
    return bool(tokens) and 2 * hits >= len(tokens)


def evidence_units(candidate: EvidenceCandidate) -> tuple[EvidenceCandidate, ...]:
    """The smallest independently verifiable requests in a suggestion (module doc).
    Empty when none is admissible (an ASK_PARENT question naming none of its fields)."""
    fields = tuple(dict.fromkeys(candidate.requested_fields))
    if candidate.acquisition_mode is AcquisitionMode.ASK_PARENT:
        question = candidate.question or ""
        fields = tuple(f for f in fields if names_field(question, f))[:1]
    return tuple(candidate.model_copy(update={"requested_fields": (f,)}) for f in fields)


@runtime_checkable
class EvidencePlanner(Protocol):
    """Suggests candidates (e.g. the Hermes runtime). Suggestions carry no authority."""

    def plan_evidence(self, context: InvestigationContext) -> tuple[EvidenceCandidate, ...]: ...


@dataclass(frozen=True, slots=True)
class ScoredCandidate:
    candidate: EvidenceCandidate
    safety: AcquisitionSafety
    evidence_required: bool
    information_value: InformationValue
    cost_micro_usd: int | None

    def key(self) -> tuple[int, int, int, int, int, int, int, str]:
        mode = self.candidate.acquisition_mode
        return (
            int(self.safety),
            0 if self.evidence_required else 1,
            _VALUE_RANK[self.information_value],
            _BURDEN_RANK[mode],
            _LATENCY_RANK[mode],
            1 if self.cost_micro_usd is None else 0,
            self.cost_micro_usd or 0,
            self.candidate.candidate_id,
        )


@dataclass(frozen=True, slots=True)
class Selection:
    """The single chosen candidate and why the rest lost. No choice means sufficient,
    unless a suggestion was refused for its form: a badly formed question is not
    evidence that nothing more is needed, so it can never complete an investigation."""

    chosen: ScoredCandidate | None
    ranked: tuple[ScoredCandidate, ...]
    excluded: tuple[tuple[str, str], ...]
    policy_version: str = POLICY_VERSION

    @property
    def sufficient(self) -> bool:
        return self.chosen is None and not any(
            reason in _NOT_SUFFICIENCY for _, reason in self.excluded
        )


class MinimumDataPolicy:
    def __init__(self, cost_model: CostModel, *, browse_allowlist: Sequence[str]) -> None:
        self._cost = cost_model
        self._allowlist = tuple(browse_allowlist)

    # ------------------------------------------------------------------ scoring
    def information_value(
        self, candidate: EvidenceCandidate, live: frozenset[str]
    ) -> InformationValue:
        expected = {p.expected for p in candidate.predictions if p.hypothesis_id in live}
        if len(expected) >= 2:
            return InformationValue.HIGH
        if expected:
            return InformationValue.MEDIUM
        return InformationValue.LOW

    def safety(self, candidate: EvidenceCandidate) -> AcquisitionSafety:
        if candidate.acquisition_mode is AcquisitionMode.BROWSE:
            inside = all(domain_allowed(d, self._allowlist) for d in candidate.allowed_domains)
            return AcquisitionSafety.SAFE if inside else AcquisitionSafety.UNSAFE
        # A question must not smuggle an intervention ("try withholding dinner...").
        screened = classify_intervention(
            Intervention(
                category=InterventionCategory.COMMUNICATION,
                description=candidate.question or "",
                reversible=True,
                max_duration_days=1,
                burden=Burden.LOW,
            )
        )
        if screened.safety_class is SafetyClass.RED:
            return AcquisitionSafety.UNSAFE
        return AcquisitionSafety.SAFE

    def score(self, candidate: EvidenceCandidate, context: InvestigationContext) -> ScoredCandidate:
        live = {b.entity_id: b for b in context.live_hypotheses()}
        predicted = {p.hypothesis_id for p in candidate.predictions if p.hypothesis_id in live}
        required = any(not live[h].supporting_evidence_ids for h in predicted)
        return ScoredCandidate(
            candidate=candidate,
            safety=self.safety(candidate),
            evidence_required=required,
            information_value=self.information_value(candidate, frozenset(live)),
            cost_micro_usd=self._cost_of(candidate),
        )

    def _cost_of(self, candidate: EvidenceCandidate) -> int | None:
        """Candidate-specific estimate if the cost table has one, else the mode's."""
        mode = f"acquire:{candidate.acquisition_mode.value}"
        specific = self._cost.estimate_cost_micro_usd(f"{mode}:{candidate.candidate_id}")
        return specific if specific is not None else self._cost.estimate_cost_micro_usd(mode)

    # ------------------------------------------------------------------ selection
    def select(
        self, candidates: Sequence[EvidenceCandidate], context: InvestigationContext
    ) -> Selection:
        excluded: list[tuple[str, str]] = []
        eligible: list[ScoredCandidate] = []
        seen: set[str] = set()
        for candidate in candidates:
            if candidate.candidate_id in seen:
                excluded.append((candidate.candidate_id, "DUPLICATE_CANDIDATE"))
                continue
            seen.add(candidate.candidate_id)
            units = evidence_units(candidate)
            if not units:
                excluded.append((candidate.candidate_id, "QUESTION_NOT_ALIGNED"))
            for unit in units:
                label = candidate.candidate_id
                if len(candidate.requested_fields) > 1:
                    label = f"{label}[{unit.requested_fields[0]}]"
                if set(unit.requested_fields) <= context.requested_fields_so_far:
                    excluded.append((label, "REDUNDANT_FIELDS"))
                    continue
                scored = self.score(unit, context)
                if scored.safety is AcquisitionSafety.UNSAFE:
                    excluded.append((label, "UNSAFE"))
                elif scored.information_value is InformationValue.LOW:
                    excluded.append((label, "LOW_VALUE"))
                else:
                    eligible.append(scored)
        # Units of one suggestion tie on every key; the stable sort keeps field order.
        ranked = tuple(sorted(eligible, key=ScoredCandidate.key))
        return Selection(
            chosen=ranked[0] if ranked else None, ranked=ranked, excluded=tuple(excluded)
        )
