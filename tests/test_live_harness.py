"""The live-eval evidence is one synthetic page, pinned by commit SHA (offline checks).

Live comparison runs read their only evidence page from an immutable
raw.githubusercontent.com URL in this public repo. These tests keep that pin
honest without touching the network: the URL names a full commit SHA, the
committed fixture is byte-identical to what was pinned, the page supports the
frozen browse oracle, and nothing but the pinned page can be re-fetched.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from eval.scenarios.runtime_live import (
    LIVE_ALLOWED,
    LIVE_PAGES_SHA,
    LIVE_SOURCES,
    _PinnedFetcher,
    live_oracle,
)
from eval.scenarios.runtime_scenarios import SCENARIOS
from serene.adapters.browser import visible_text
from serene.domain.canonical import sha256_hex
from serene.policies.external_evidence import host_of
from tests.evidence_support import EXCERPT

ROOT = Path(__file__).resolve().parents[1]
# sha256 of eval/fixtures/pages/daycare-pickup-policy.html at LIVE_PAGES_SHA, as served
# by raw.githubusercontent.com on 2026-10-10. Editing the fixture needs a new pin.
PINNED_PAGE_SHA256 = "c2be99557c2396a3145f98d8524b630dca74475b6932b311a861e800bf4614b5"


def test_live_evidence_is_one_sha_pinned_page_from_this_repo() -> None:
    (url,) = LIVE_SOURCES
    prefix = f"https://raw.githubusercontent.com/Sathvikar01/morrow/{LIVE_PAGES_SHA}/"
    assert len(LIVE_PAGES_SHA) == 40 and url.startswith(prefix)
    assert host_of(url) in LIVE_ALLOWED and LIVE_ALLOWED == ("raw.githubusercontent.com",)
    page = (ROOT / url.removeprefix(prefix)).read_bytes()
    assert sha256_hex(page) == PINNED_PAGE_SHA256  # the committed fixture is what was pinned


def test_pinned_page_supports_the_frozen_browse_oracle() -> None:
    (url,) = LIVE_SOURCES
    prefix = f"https://raw.githubusercontent.com/Sathvikar01/morrow/{LIVE_PAGES_SHA}/"
    text = visible_text((ROOT / url.removeprefix(prefix)).read_text(encoding="utf-8"))
    assert EXCERPT in text and "2026-09-01" in text


def test_verifier_refetch_reads_nothing_but_the_pinned_page() -> None:
    fetcher = _PinnedFetcher()
    other = "https://raw.githubusercontent.com/Sathvikar01/morrow/main/README.md"
    assert fetcher.fetch(other, LIVE_ALLOWED) is None  # refused before any network access


def test_live_oracle_only_moves_the_browse_allowlist() -> None:
    for sid, scenario in SCENARIOS.items():
        frozen, live = scenario.oracle, live_oracle(sid)
        expected = LIVE_ALLOWED if frozen.allowed_domains else ()
        assert live.allowed_domains == expected
        assert dataclasses.replace(live, allowed_domains=frozen.allowed_domains) == frozen


class _RecordingSink:
    def __init__(self) -> None:
        self.session_id: str | None = None
        self.pending: list[tuple[str, dict[str, object]]] = []
        self.posted: list[list[tuple[str, dict[str, object]]]] = []

    def emit(self, name: str, attributes: dict[str, object]) -> None:
        self.pending.append((name, attributes))

    def flush(self) -> bool:
        self.posted.append(self.pending)
        self.pending = []
        return True


def test_neatlogs_upload_is_split_under_the_ingest_body_limit(monkeypatch: Any) -> None:
    from eval.runners import runtime_live_compare as runner
    from serene.adapters import neatlogs_sink

    sink = _RecordingSink()
    monkeypatch.setenv("NEATLOGS_API_KEY", "test-not-a-key")
    monkeypatch.setattr(neatlogs_sink, "build_sink", lambda _name: sink)
    traces = [("runtime.call", {"event_id": f"evt_{i:032x}", "status": "OK"}) for i in range(200)]
    out = runner._neatlogs("run-1", SimpleNamespace(traces=traces))  # type: ignore[arg-type]
    assert out == {
        "sent": True,
        "session_id": "run-1",
        "spans": 200,
        "batches": len(sink.posted),
        "batches_sent": len(sink.posted),
    }
    assert sink.session_id == "run-1" and len(sink.posted) > 1
    assert [t for batch in sink.posted for t in batch] == traces  # nothing lost or reordered
    for batch in sink.posted:
        size = sum(len(json.dumps({"name": n, "attributes": a})) for n, a in batch)
        assert size <= runner._NEATLOGS_BATCH_BYTES
