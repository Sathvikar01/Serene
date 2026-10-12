"""Build a judge bundle only after the canonical demo and every checklist item pass."""

from __future__ import annotations

import io
import json
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from scripts import docs_check
from serene.demo.maya import SEED
from serene.demo.report import render_html, verify_report
from serene.demo.reset import demo_directory
from serene.domain.canonical import canonical_json

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = frozenset(
    [f"M{number:02d}" for number in range(1, 19)]
    + [
        "RESET",
        "PRIVACY",
        "CI",
        "NEATLOGS",
        "EVAL",
        "IMPROVEMENT",
        "ENTIRE",
        "CFO",
        "README",
        "PUBLIC_BUILD",
        "RECORDING",
        "BACKUP",
        "SUBMISSION",
    ]
)
ITEM = re.compile(r"^- \[([ x])\] \*\*([A-Z_0-9]+)\*\*: (.+)$", re.M)


def checklist_blockers(text: str) -> list[str]:
    rows = ITEM.findall(text)
    ids = [item_id for _, item_id, _ in rows]
    if len(ids) != len(set(ids)) or set(ids) != REQUIRED:
        raise ValueError("Checklist IDs missing, duplicated or unexpected")
    if any(not docs_check.LINK.search(description) for _, _, description in rows):
        raise ValueError("Every checklist item requires an evidence link")
    return [item_id for checked, item_id, _ in rows if checked != "x"]


def build_release(root: Path) -> list[str]:
    """No network, evaluation execution, production data or arbitrary CLI output path."""
    directory = demo_directory(root)
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / "judge-demo.zip"
    temporary = directory / "judge-demo.tmp"
    for path in (destination, temporary):
        if path.is_symlink() or path.resolve() != path:
            raise ValueError("Release artifact must not be a link")
    # Withdraw any older release before validating this build; failures leave no bundle.
    destination.unlink(missing_ok=True)
    temporary.unlink(missing_ok=True)
    if not __debug__:
        raise ValueError("Release verification requires Python assertions enabled")
    checklist = root / "docs" / "demo-acceptance.md"
    text = checklist.read_text(encoding="utf-8")
    blockers = checklist_blockers(text)
    link_failures = docs_check.check_links((checklist,))
    if link_failures:
        raise ValueError("Checklist evidence paths or anchors do not resolve")
    report_bytes = (directory / "report.json").read_bytes()
    report = json.loads(report_bytes)
    if report["seed"] != SEED:
        raise ValueError("Not the canonical synthetic Maya seed")
    verify_report(report)  # Existing domain/event/order verification, never a success flag.
    if blockers:
        return blockers
    contents = {
        "report.json": canonical_json(report) + b"\n",
        "report.html": render_html(report).encode("utf-8"),
        "demo-acceptance.md": text.encode("utf-8"),
        "README.md": (root / "README.md").read_bytes(),
    }
    buffer = io.BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as archive:
        for name, data in sorted(contents.items()):
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    temporary.write_bytes(buffer.getvalue())
    temporary.replace(destination)
    return []


def main() -> int:
    try:
        blockers = build_release(ROOT)
    except (AssertionError, OSError, ValueError, KeyError, TypeError) as error:
        print(f"Demo release BLOCKED: {type(error).__name__}; check fixture/evidence")
        return 1
    if blockers:
        print(f"Demo release BLOCKED: {', '.join(blockers)}")
        return 1
    print("Demo release READY: .demo/maya/judge-demo.zip")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
