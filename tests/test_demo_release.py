"""Release acceptance reuses the real fixture; no mock domain runtime or eval execution."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import pytest

from scripts import demo_release, docs_check
from serene.demo.maya import MayaDemo


@pytest.fixture(scope="module")
def maya_report(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    return MayaDemo(tmp_path_factory.mktemp("release-memory")).run()


@pytest.fixture
def release_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, maya_report: dict[str, Any]
) -> Path:
    monkeypatch.setattr(docs_check, "ROOT", tmp_path)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "proof.md").write_text("# Synthetic test receipt\n", encoding="utf-8")
    checklist = "\n".join(
        f"- [x] **{item_id}**: Test-only signoff [evidence](proof.md)."
        for item_id in sorted(demo_release.REQUIRED)
    )
    (tmp_path / "docs" / "demo-acceptance.md").write_text(checklist, encoding="utf-8")
    (tmp_path / "README.md").write_text("Synthetic test README", encoding="utf-8")
    directory = tmp_path / ".demo" / "maya"
    directory.mkdir(parents=True)
    (directory / "report.json").write_text(json.dumps(maya_report), encoding="utf-8")
    return tmp_path


def test_real_checklist_has_all_beats_and_supporting_evidence() -> None:
    path = demo_release.ROOT / "docs" / "demo-acceptance.md"
    assert docs_check.check_links((path,)) == []
    assert set(demo_release.checklist_blockers(path.read_text(encoding="utf-8"))) == {
        "IMPROVEMENT",
        "ENTIRE",
        "PUBLIC_BUILD",
        "RECORDING",
        "BACKUP",
        "SUBMISSION",
    }


@pytest.mark.parametrize("item_id", sorted(demo_release.REQUIRED))
def test_each_unchecked_item_blocks_and_withdraws_old_bundle(
    release_root: Path, item_id: str
) -> None:
    checklist = release_root / "docs" / "demo-acceptance.md"
    checklist.write_text(
        checklist.read_text().replace(f"[x] **{item_id}**", f"[ ] **{item_id}**"),
        encoding="utf-8",
    )
    bundle = release_root / ".demo" / "maya" / "judge-demo.zip"
    bundle.write_bytes(b"stale release")
    assert demo_release.build_release(release_root) == [item_id]
    assert not bundle.exists()


def test_missing_duplicate_or_unlinked_item_is_not_a_pass(release_root: Path) -> None:
    text = (release_root / "docs" / "demo-acceptance.md").read_text()
    for invalid in (
        "\n".join(text.splitlines()[1:]),
        text + "\n" + text.splitlines()[0],
        text.replace("[evidence](proof.md)", "unverified", 1),
    ):
        with pytest.raises(ValueError):
            demo_release.checklist_blockers(invalid)


def test_all_reviewed_items_build_identical_bundle_from_verified_json(release_root: Path) -> None:
    directory = release_root / ".demo" / "maya"
    (directory / "report.html").write_text("counterfeit HTML", encoding="utf-8")
    assert demo_release.build_release(release_root) == []
    bundle = directory / "judge-demo.zip"
    first = bundle.read_bytes()
    assert demo_release.build_release(release_root) == []
    assert bundle.read_bytes() == first
    with ZipFile(bundle) as archive:
        assert set(archive.namelist()) == {
            "README.md",
            "demo-acceptance.md",
            "report.html",
            "report.json",
        }
        assert b"counterfeit HTML" not in archive.read("report.html")
        assert b"All 18 beats passed" in archive.read("report.html")


def test_checked_items_cannot_admit_tampered_domain_evidence(release_root: Path) -> None:
    directory = release_root / ".demo" / "maya"
    assert demo_release.build_release(release_root) == []
    report_path = directory / "report.json"
    report = json.loads(report_path.read_bytes())
    report["events"][0]["payload"]["tampered"] = True
    report_path.write_text(json.dumps(report), encoding="utf-8")
    with pytest.raises(ValueError):
        demo_release.build_release(release_root)
    assert not (directory / "judge-demo.zip").exists()


def test_broken_evidence_link_blocks_checked_item(release_root: Path) -> None:
    (release_root / "docs" / "proof.md").unlink()
    with pytest.raises(ValueError, match="evidence paths"):
        demo_release.build_release(release_root)


def test_documented_module_entrypoint_reaches_gate_without_import_error() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "scripts.demo_release"],
        cwd=demo_release.ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert result.returncode == 1
    assert result.stdout.startswith("Demo release BLOCKED:")
    assert result.stderr == ""
