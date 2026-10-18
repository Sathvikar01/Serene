# Canonical integration verification — 17–18 October 2026

Started from freshly fetched `origin/main` at `d90c227` in an isolated worktree,
after reading `CLAUDE.md`, `AGENTS.md`, architecture, runtime, evidence, safety,
Maya and existing web/hosted proof documentation. The existing checkout was left
untouched. That main revision's most recent GitHub CI run was already green:
[38293725801](https://github.com/Sathvikar01/Serene/actions/runs/38293725801).

## Reproductions and causes

Before implementation, the baseline commands found:

| Check | Baseline result |
| --- | --- |
| `npm run typecheck` | PASS |
| `npm test` | 274 PASS |
| `npm run build` | PASS when run alone |
| `npm run test:e2e` | 138 passed, three existing viewport skips, one mobile Twin hydration failure (React #418, at the unchanged clean-console assertion) |
| `uv run pytest` | 1,473 passed, one Windows symlink-permission skip; `test_identity_git_completes_while_private_stdin_read_is_pending[clean]` exceeded its 20-second queue deadline |
| Ruff, mypy, ledger self-check, secret scan | PASS |
| Inspect invariant gate / core report | 20/20 CORRECT / 10/10 PASS |

An initial overlapping build attempt lost `.next/server/pages-manifest.json`.
This was an execution mistake, not an application root cause; the isolated build
passed. The private-stdin regression's two cases passed in isolation without
changing its timeout, implementation or evaluation protocol. The mobile Twin
check also passed three isolated production repetitions. The stdin timeout did
not recur in the complete final backend suite (1,481 passed, one existing
Windows symlink-permission skip); no domain rule or timeout was changed.

Full browser diagnostics later captured React expecting the AppShell `div`
while its hydration cursor was at `head > meta`. RootLayout imported
`BLOOM_SCRIPT` from a `"use client"` module: the Flight payload supplied `"$2"`
as the inline script rather than script text. A late module can suspend `head`
and trigger React's singleton cursor replay bug
([upstream reproduction](https://github.com/react/react/issues/37551)). The
bootstrap constant now lives in the server layout; its behavior is identical
and the head no longer depends on that client export. A production HTTP
regression failed before the fix with `Received string: "$2"` and requires
the bootstrap text in the initial Flight payload.

The canonical-state audit then reproduced three integration defects:

1. Superseding a hypothesis produced policy/Twin `NEEDS_REVIEW`, while saved
   Memory and retrieved belief still said `ACTIVE`. The read paths used document
   front matter or a date-only helper instead of the owning learning-validity
   policy. Memory views, published learning rows and retrieved belief now use
   `serene.policies.learning.effective_status`. Snapshot views evaluate at the
   ledger head time; retrieved belief uses the supplied retrieval time. Git
   document bytes are retained; this does not write a new learning or memory.
2. The Maya adapter accepted appended unreviewed memory prose and a substituted
   memory revision, despite a valid event hash chain. It now reconstructs the
   document set and per-file revisions from committed patch events, checks patch
   preimages, and refuses a report snapshot/head that disagrees.
3. Maya's introductory summary and chapter takeaways repeated hardcoded success
   prose. They now display the validated investigation question, trial/approval
   stage, recorded outcomes, memory/status, rejection rationale and Twin verdicts.
   Earlier checkpoint selection remains scoped to the investigation; that scope
   is now stated explicitly beside the selector.

## Regression coverage

- Five real-ledger/Git cases: supersession, contradicting outcome, refutation,
  context drift and overdue review. Memory, retrieved belief, published learning
  status and Twin agree before timers or memory rewriting. Historical Git bytes
  and ledger hashes remain intact.
- The PostgreSQL publisher/backfill test now appends a supersession and checks
  the saved Memory projection updates without changing its pinned Git revision.
- Two adapter regressions reject altered memory text and revision receipts.
- The existing clean reset → Maya → report → UI browser journey additionally
  compares its summary with canonical backend fields. Original evidence,
  approval, outcome, Dream, promotion and provenance assertions remain intact.
- The three existing viewport skips are removed: phone-map checks explicitly
  select phone widths, and the menu test resizes when the inline nav is shown.
  No assertion is weakened and no sleep or production test branch is added.
- The production shell payload must contain the inline bootstrap text, without
  requiring a client module to resolve inside `head`. Existing clean-console
  browser assertions continue to catch hydration errors.
- Memory's keyboard provenance check explicitly waits for one patch target
  after native fragment activation, before the unchanged viewport and status
  checks. A CI trace caught two transient matches while hydration finished;
  its final snapshot held one visible article. No duplicate is selected away.

## Files changed

| Path | Change |
| --- | --- |
| `app/web/app/demo/maya/MayaDemoView.tsx` | Render summaries from validated domain views and clarify checkpoint scope |
| `app/web/app/layout.tsx`, `app/web/components/brand/BloomDirector.tsx` | Keep the inline head bootstrap server-owned to avoid a hydration race |
| `scripts/maya_web_state.py` | Bind report memory text and per-file revisions to committed patch events |
| `serene/memory/view.py` | Derive current learning status from canonical validity policy |
| `serene/projections/memory.py` | Remove the conflicting date-only status override |
| `serene/projections/views.py` | Publish effective learning status at the ledger head |
| `serene/investigation/context.py` | Retrieve belief with the owning validity policy |
| `tests/test_memory_projection.py` | Five correction cases and PostgreSQL publication/backfill regression |
| `tests/test_maya_web_state.py` | Reject tampered memory text/revision receipts |
| `app/web/e2e/maya-demo.spec.ts` | Compare the summary against canonical backend fields |
| `app/web/e2e/memory.spec.ts` | Require one provenance target before checking native fragment navigation |
| `app/web/e2e/causal-twin.spec.ts`, `app/web/e2e/shell.spec.ts` | Exercise viewport cases instead of skipping them; verify the head bootstrap arrives as text |
| `docs/canonical-integration-validation.md` | Reproduction, verification and integration evidence boundaries |

## Verification commands

Run Python commands at repository root, web commands in `app/web`. CI uses locked
Python 3.11 and Node 20; local reproduction uses Windows, Python 3.11 and Node 24.

```sh
uv sync --locked --all-extras --group dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python scripts/ledger_selfcheck.py
uv run python scripts/secret_scan.py
uv run python scripts/env_audit.py
uv run python scripts/synthetic_audit.py
uv run python scripts/docs_check.py
uv run python scripts/economics_report.py --check
```

```sh
uv run inspect eval eval/tasks/kernel_invariants.py --model mockllm/model --log-dir eval/reports/local/final --display plain
uv run inspect eval eval/tasks/trust_invariants.py --model mockllm/model --log-dir eval/reports/local/final --display plain
uv run inspect eval eval/tasks/runtime_investigation.py --model mockllm/model --log-dir eval/reports/local/final --display plain
uv run python scripts/inspect_gate.py eval/reports/local/final kernel_invariants trust_invariants runtime_investigation
uv run inspect eval eval/tasks/core_scenarios.py --model mockllm/model --log-dir eval/reports/local/final --display plain
uv run python eval/runners/core_scenarios_report.py eval/reports/local/final
```

```sh
npm ci
npm run typecheck
npm test
npm run build
npx playwright install chromium
npm run test:e2e
npm run test:e2e:approvals
```

After the approvals lane, reuse its identical build for the Twin lane:
`SERENE_E2E_SKIP_BUILD=1 npm run test:e2e:twin` (PowerShell: set
`$env:SERENE_E2E_SKIP_BUILD='1'` before running the npm command).

Final run receipts are recorded in the PR verification section. The configured
GitHub workflow runs all four required jobs from clean checkouts; it does not
require hosted credentials.

## Integration evidence and limits

| Integration | What this pass can establish |
| --- | --- |
| Hermes/agent boundary | Scripted wire, admission, trust and runtime regressions; no new live provider run |
| Supabase/PostgreSQL | Real disposable local PostgreSQL, migrations, RLS, ledger/publisher/backfill tests and synthetic-Auth browser lanes; hosted credentials are absent, so the opt-in hosted lane is not repeated |
| Causal Twin | Canonical relationship/validity/provenance builders and browser checks; unnamed production variables remain listed rather than assigned guessed endpoints |
| Memory/Dream | Real Git commits, Critic/approval gates, pinned snapshot publication and correction regressions |
| NeatLogs | Adapter, recording-sink, redaction and failure-isolation tests; no new live export receipt |
| Entire | Enabled CLI 0.11.4, pushing disabled; read-only `checkpoint explain ... --json` succeeds for both existing records below; no new checkpoint or complete milestone coverage is claimed |
| cfo.ai | Existing scenario artifacts plus reproducible local assumed-economics report; no new remote scenario or measured billing claim |

Existing Entire records checked with `entire checkpoint explain <id> --json`:
`01M4JMP49DYR5MABPHPD1RPT0J` (12 checkpoints, one session) and
`01M4JGDW740K8ENKH3GYRJEH15` (eight checkpoints, one session). These envelope
counts are not counts of completed milestones. Private outputs stay local.

PR #67 was checked with `gh pr view 67 --json state,mergedAt,url`: CLOSED,
`mergedAt=null`. Its change remains unmerged and its evidence DEV-only.
Evaluation protocols, scorers, holdout results and archived evidence are unchanged.
The documented empty-plan completion limitation, ledger-head snapshot timing,
non-atomic Git/Postgres publication and incomplete Entire coverage remain visible.
