"""Run the frozen runtime scenarios against a LIVE Hermes for Serene and Baselines A/B.

    set -a; . ./.env.local; set +a          # HERMES_API_SERVER_KEY, HERMES_API_BASE_URL
    uv run python eval/runners/runtime_live_compare.py --label before

No scripted replies: every model call goes to the Hermes API server. Writes,
under eval/reports/local/live/<label>-<utc>/:

    manifest.json           versions, budget, faults, endpoint health, git state
    scores.json             deterministic scorer rows (standard format) + summary
    raw/<system>__<scenario>.jsonl     every model exchange, verbatim
    traces/serene__<scenario>.jsonl    SafeTelemetry records (already redacted)

When NEATLOGS_API_KEY is set the same redacted records are also sent to
neatlogs through `serene.adapters.neatlogs_sink.build_sink`, in traces under
~8 KiB that share one session id: the run id is the neatlogs session handle.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eval.baselines.runtime_baselines import BASELINE_PROMPT_VERSION, MatchedBudget  # noqa: E402
from eval.scenarios.runtime_live import (  # noqa: E402
    FAULTS,
    LIVE_ALLOWED,
    LIVE_SOURCES,
    PARENT_FACTS,
    SYSTEMS,
    LiveResult,
    live_oracle,
)
from eval.scenarios.runtime_scenarios import SCENARIOS  # noqa: E402
from eval.scorers.runtime_scorers import SCORER_VERSION, report_row  # noqa: E402
from serene.adapters.browser.hermes_browser import BROWSER_PROMPT_VERSION  # noqa: E402
from serene.adapters.hermes import transport_from_env  # noqa: E402
from serene.adapters.hermes.runtime import PROMPT_VERSION  # noqa: E402

# neatlogs ingest answers HTTP 403 to request bodies over ~8 KiB (measured 2026-10-10:
# 8150 bytes accepted, 8364 refused), so one run goes out as several traces that share
# the run's session id. Records are counted before the sink's own envelope, hence margin.
_NEATLOGS_BATCH_BYTES = 5_500


def _git() -> dict[str, Any]:
    def run(*args: str) -> str:
        return subprocess.run(  # noqa: S603 - fixed git read-only arguments
            ["git", *args],  # noqa: S607 - git from PATH, as every developer command
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()

    return {"head": run("rev-parse", "HEAD"), "dirty": bool(run("status", "--porcelain"))}


def _health() -> Any:
    base = (os.environ.get("HERMES_API_BASE_URL") or "http://127.0.0.1:8642/v1").rstrip("/")
    url = base.removesuffix("/v1") + "/health"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:  # noqa: S310 - loopback/https only
            return json.loads(resp.read(65_536).decode("utf-8"))
    except Exception as exc:  # health is informational only
        return {"error": type(exc).__name__}


def _neatlogs(run_id: str, result: LiveResult) -> dict[str, Any]:
    if not os.environ.get("NEATLOGS_API_KEY") or not result.traces:
        return {"sent": False, "reason": "NEATLOGS_API_KEY unset" if result.traces else "no traces"}
    from serene.adapters.neatlogs_sink import build_sink

    sink = build_sink("serene-live-eval")
    if hasattr(sink, "session_id"):  # HTTP sink: the run id is the neatlogs session handle
        sink.session_id = run_id
    flush = getattr(sink, "flush", None)
    batches = sent = size = 0
    for name, attrs in result.traces:  # already redacted by SafeTelemetry
        record = len(json.dumps({"name": name, "attributes": attrs}, default=str))
        if callable(flush) and size and size + record > _NEATLOGS_BATCH_BYTES:
            batches, sent, size = batches + 1, sent + bool(flush()), 0
        sink.emit(name, attrs)
        size += record
    if callable(flush) and size:
        batches, sent = batches + 1, sent + bool(flush())
    return {
        "sent": sent == batches if callable(flush) else True,
        "session_id": run_id,
        "spans": len(result.traces),
        "batches": batches,
        "batches_sent": sent,
    }


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_system: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_system[row["system"]].append(row)
    out: dict[str, Any] = {}
    for system, items in by_system.items():
        dims = sorted({d for r in items for d in r["scores"]})
        out[system] = {
            "runs": len(items),
            "mean": {
                d: round(sum(r["scores"][d]["value"] for r in items) / len(items), 4) for d in dims
            },
            "passed": {d: sum(1 for r in items if r["scores"][d]["passed"]) for d in dims},
            "critical_findings": sum(
                len(s["critical"]) for r in items for s in r["scores"].values()
            ),
            "terminal": dict(Counter(r["terminal"] for r in items)),
            "model_calls": sum(r["budget"]["model_calls"] for r in items),
            "input_tokens": sum(r["live"]["input_tokens"] for r in items),
            "output_tokens": sum(r["live"]["output_tokens"] for r in items),
            "transport_errors": sum(r["live"]["transport_errors"] for r in items),
            "wall_ms": sum(r["live"]["wall_ms"] for r in items),
        }
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True)
    parser.add_argument("--systems", default=",".join(SYSTEMS))
    parser.add_argument("--scenarios", default=",".join(SCENARIOS))
    args = parser.parse_args(argv)
    live = transport_from_env()
    if live is None:
        print("UNAVAILABLE: HERMES_API_SERVER_KEY is not set; no live run, no numbers.")
        return 2
    started = datetime.now(UTC)
    out = ROOT / "eval" / "reports" / "local" / "live" / f"{args.label}-{started:%Y%m%dT%H%M%SZ}"
    (out / "raw").mkdir(parents=True)
    (out / "traces").mkdir()
    rows: list[dict[str, Any]] = []
    models: set[str] = set()
    for sid in args.scenarios.split(","):
        for system in args.systems.split(","):
            run_id = f"{out.name}__{system}__{sid}"
            result = SYSTEMS[system](sid, live)
            row = report_row(result.trajectory, live_oracle(sid))
            ok = [e["response"] for e in result.exchanges if "response" in e]
            models |= {str(r["model"]) for r in ok if r["model"]}
            row["mode"] = "live-model"
            row["run_id"] = run_id
            row["terminal"] = result.trajectory.terminal
            row["failures_recorded"] = list(result.trajectory.failures_recorded)
            row["notes"] = result.notes
            row["live"] = {
                "exchanges": len(result.exchanges),
                "transport_errors": sum(1 for e in result.exchanges if "error" in e),
                "input_tokens": sum(r["usage"]["input_tokens"] or 0 for r in ok),
                "output_tokens": sum(r["usage"]["output_tokens"] or 0 for r in ok),
                "wall_ms": result.wall_ms,
            }
            row["neatlogs"] = _neatlogs(run_id, result)
            rows.append(row)
            stem = f"{system}__{sid}"
            with (out / "raw" / f"{stem}.jsonl").open("w", encoding="utf-8") as fh:
                for exchange in result.exchanges:
                    fh.write(json.dumps(exchange, ensure_ascii=False) + "\n")
            if result.traces:
                with (out / "traces" / f"{stem}.jsonl").open("w", encoding="utf-8") as fh:
                    for name, attrs in result.traces:
                        record = {"name": name, "attributes": attrs}
                        fh.write(json.dumps(record, default=str) + "\n")
            print(
                f"{system:<30} {sid:<26} terminal={row['terminal']:<18} "
                + " ".join(f"{k}={v['value']:.2f}" for k, v in row["scores"].items())
                + f" calls={row['budget']['model_calls']} errors={row['live']['transport_errors']}"
            )
    manifest = {
        "label": args.label,
        "started_at": started.isoformat(),
        "finished_at": datetime.now(UTC).isoformat(),
        "git": _git(),
        "hermes": {
            "base_url": os.environ.get("HERMES_API_BASE_URL"),
            "health": _health(),
            "served_models": sorted(models),
        },
        "versions": {
            "scorer": SCORER_VERSION,
            "runtime_prompt": PROMPT_VERSION,
            "browser_prompt": BROWSER_PROMPT_VERSION,
            "baseline_prompt": BASELINE_PROMPT_VERSION,
        },
        "matched_budget": MatchedBudget.from_serene().__dict__,
        "faults": {sid: FAULTS[sid].__dict__ for sid in args.scenarios.split(",")},
        "parent_facts": {sid: PARENT_FACTS[sid] for sid in args.scenarios.split(",")},
        "evidence_sources": list(LIVE_SOURCES),
        "browse_allowlist": list(LIVE_ALLOWED),
        "sampling": "Hermes server defaults (not pinned by the client)",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str), "utf-8")
    report = {"rows": rows, "summary": _summary(rows)}
    (out / "scores.json").write_text(json.dumps(report, indent=2, sort_keys=True), "utf-8")
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
