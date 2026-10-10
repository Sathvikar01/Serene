"""Versioned wire contract between Serene and the Hermes model (structured output).

The model never sees or mints kernel identifiers for new objects: it refers to
new items with short local refs ("P1", "H2") and to existing ones only by ids
that were present in its rendered context. The adapter then mints ids,
attaches provenance and builds kernel entities; the kernel boundary admits.

Validation is staged and fails closed:
  1. byte bound and an optional single ```json fence (the only normalization);
  2. JSON with duplicate keys or non-finite numbers is rejected;
  3. strict schema (closed variants, bounded lengths, no extra fields,
     contract version must match exactly);
  4. semantic checks (ref resolution, visibility, evidence status) in the runtime.
"""

from __future__ import annotations

import json
import re
from datetime import date
from typing import Annotated, Any, Final, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError

from serene.domain.base import ShortText, Tag
from serene.domain.entities import Burden, InterventionCategory
from serene.domain.events import AcquisitionMode, PredictedAnswer

WIRE_VERSION: Final = "serene-hermes-wire/1"
MAX_WIRE_BYTES: Final = 64_000

LocalRef = Annotated[str, StringConstraints(pattern=r"^[A-Z][A-Za-z0-9]{0,7}$")]
KernelRef = Annotated[str, StringConstraints(pattern=r"^[a-z]{3}_[0-9a-f]{32}$")]
Ref = LocalRef | KernelRef
HttpsUrl = Annotated[str, StringConstraints(pattern=r"^https://[^\s]{1,2000}$")]


class _Wire(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class WireObservation(_Wire):
    kind: Literal["observation"]
    evidence_ids: tuple[KernelRef, ...] = Field(min_length=1, max_length=8)
    statement: ShortText
    contexts: tuple[Tag, ...] = Field(default=(), max_length=8)


class WirePattern(_Wire):
    kind: Literal["pattern"]
    ref: LocalRef
    observation_ids: tuple[KernelRef, ...] = Field(min_length=2, max_length=32)
    counter_observation_ids: tuple[KernelRef, ...] = Field(default=(), max_length=32)
    description: ShortText
    contexts: tuple[Tag, ...] = Field(default=(), max_length=8)


class WireHypothesis(_Wire):
    kind: Literal["hypothesis"]
    ref: LocalRef
    pattern_refs: tuple[Ref, ...] = Field(min_length=1, max_length=8)
    statement: ShortText
    supporting_evidence_ids: tuple[KernelRef, ...] = Field(default=(), max_length=32)
    counter_evidence_ids: tuple[KernelRef, ...] = Field(default=(), max_length=32)
    alternative_explanations: tuple[ShortText, ...] = Field(default=(), max_length=8)
    known_confounders: tuple[ShortText, ...] = Field(default=(), max_length=8)
    falsification_criteria: tuple[ShortText, ...] = Field(min_length=1, max_length=4)
    contexts: tuple[Tag, ...] = Field(min_length=1, max_length=8)
    supersedes: KernelRef | None = None


class WireExperiment(_Wire):
    kind: Literal["experiment"]
    hypothesis_ref: Ref
    category: InterventionCategory
    description: ShortText
    reversible: bool
    max_duration_days: int = Field(ge=1, le=365)
    burden: Burden
    comparison: ShortText
    outcome_measure: ShortText


class WireNeedEvidence(_Wire):
    kind: Literal["need_evidence"]
    requested_fields: tuple[Tag, ...] = Field(min_length=1, max_length=8)
    rationale: ShortText


class WireAbstain(_Wire):
    kind: Literal["abstain"]
    reason: ShortText


WireProposal = Annotated[
    WireObservation
    | WirePattern
    | WireHypothesis
    | WireExperiment
    | WireNeedEvidence
    | WireAbstain,
    Field(discriminator="kind"),
]


class WireProposals(_Wire):
    contract: Literal["serene-hermes-wire/1"]
    proposals: tuple[WireProposal, ...] = Field(max_length=16)


class WirePrediction(_Wire):
    hypothesis_id: KernelRef
    expected: PredictedAnswer


class WireCandidate(_Wire):
    candidate_id: Annotated[str, StringConstraints(pattern=r"^[a-z0-9_\-]{1,64}$")]
    requested_fields: tuple[Tag, ...] = Field(min_length=1, max_length=8)
    acquisition_mode: AcquisitionMode
    rationale: ShortText
    question: ShortText | None = None
    subject: Tag | None = None
    allowed_domains: tuple[
        Annotated[str, StringConstraints(pattern=r"^[a-z0-9.\-]{1,253}$")], ...
    ] = Field(default=(), max_length=8)
    predictions: tuple[WirePrediction, ...] = Field(default=(), max_length=8)


class WirePlan(_Wire):
    contract: Literal["serene-hermes-wire/1"]
    candidates: tuple[WireCandidate, ...] = Field(max_length=8)


class WireCapture(_Wire):
    url: HttpsUrl
    subject: Tag
    effective_date: date
    fields: dict[Tag, ShortText] = Field(max_length=16)
    excerpt: Annotated[str, StringConstraints(min_length=1, max_length=2000)]


class WireBrowseReport(_Wire):
    contract: Literal["serene-hermes-wire/1"]
    captures: tuple[WireCapture, ...] = Field(max_length=4)


class WireError(ValueError):
    """Machine-readable parse/schema failure. Never echoes model text."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


_FENCE = re.compile(r"^\s*```(?:json)?\s*\n(.*)\n\s*```\s*$", re.S)


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise WireError("DUPLICATE_KEY")
    return dict(pairs)


def _reject_constant(_: str) -> Any:
    raise WireError("NON_FINITE_NUMBER")


M = TypeVar("M", bound=_Wire)


def parse_wire(text: str, model: type[M]) -> M:
    if len(text.encode("utf-8")) > MAX_WIRE_BYTES:
        raise WireError("TOO_LARGE")
    fenced = _FENCE.match(text)
    body = fenced.group(1) if fenced else text.strip()
    if not body:
        raise WireError("EMPTY")
    try:
        json.loads(body, object_pairs_hook=_reject_duplicates, parse_constant=_reject_constant)
    except WireError:
        raise
    except ValueError:
        raise WireError("NOT_JSON") from None
    try:
        return model.model_validate_json(body)
    except ValidationError as exc:
        first = exc.errors()[0]
        if first.get("loc") and first["loc"][0] == "contract":
            raise WireError("UNKNOWN_CONTRACT_VERSION") from None
        raise WireError(f"SCHEMA:{first.get('type', 'invalid')}") from None
