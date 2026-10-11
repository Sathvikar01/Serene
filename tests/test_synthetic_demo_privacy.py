"""The canonical demo uses synthetic sources and cannot upload private narratives."""

import json
import socket
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from serene.demo.maya import MayaDemo


def test_full_demo_stays_offline_and_telemetry_contains_no_narratives(
    tmp_path: Path, monkeypatch: Any
) -> None:
    def forbidden(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("Canonical synthetic demo attempted network access")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    demo = MayaDemo(tmp_path / "memory")
    report = demo.run()
    assert report["synthetic"] and report["mode"] == "offline-scripted-io"
    traces = json.dumps(demo.sink.records)
    assert demo.sink.records and demo.family.child_id not in traces
    for event in report["events"]:
        if event["source"].get("uri"):
            assert urlparse(event["source"]["uri"]).hostname == "example.org"
        evidence = event["payload"].get("evidence")
        if evidence is not None:
            assert evidence["content"] not in traces
    assert "Synthetic Maya" not in traces and "every transition everywhere" not in traces


def test_preserved_eval_pages_and_tapes_declare_synthetic_data() -> None:
    # Read existing provenance declarations; do not open the holdout or alter frozen artifacts.
    root = Path(__file__).resolve().parents[1]
    page = root / "eval/fixtures/pages/daycare-pickup-policy.html"
    assert "SYNTHETIC EVALUATION FIXTURE" in page.read_text(encoding="utf-8")
    for version in (3, 4, 5):
        metadata = root / f"eval/fixtures/shared-prefix-dev-v{version}-experiment.json"
        assert "synthetic_DEV_only_no_secrets_or_family_data" in metadata.read_text(
            encoding="utf-8"
        )
    web = json.loads((root / "app/web/fixtures/synthetic-causal-twin.json").read_bytes())
    assert web["child_id"] == "chd_" + "0" * 31 + "1"
