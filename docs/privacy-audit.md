# Secrets, privacy and logging audit (#59)

Audit date: 12 October 2026 (Asia/Kolkata). Scope: the merged code plus canonical
Maya demo/reset. This is a time-boxed repository audit, not a system redesign.

**Status: incomplete.** This PR supplies the frontend/error and environment
coverage corrections. A separate active audit on `chore/privacy-secrets-audit-59`
has identified further defects and owns additional corrections. Do not merge
conflicting #59 work or close #59 until the full acceptance criteria are proven.

## Findings and fixes

| Check | Evidence/result |
| --- | --- |
| Current repository credentials/PII patterns | `scripts/secret_scan.py`: zero findings over tracked and nonignored untracked text files |
| Credentials in merged history | Read-only `git log -p --format= --no-ext-diff origin/main`, scanned with the same credential patterns excluding attribution-email checks: zero matches |
| Environment coverage | `tests/test_repo_hygiene.py` covers backend, scripts, eval, Telegram and web environment reads; `.env.example` now includes `SERENE_FIXTURE_ROUTES`, `CI` and Inspect's `INSPECT_LOGS` |
| Secret template values | Existing test requires KEY/TOKEN/SECRET/PASSWORD values to remain empty |
| Backend/runtime redaction | Existing observability, runtime-tracing and NeatLogs tests pass; unknown keys and prose values are dropped and child ids are pseudonymized/dropped |
| NeatLogs sink boundary | Existing `test_the_sink_reapplies_central_redaction` verifies direct callers cannot bypass the central redaction path; redirect/key handling and failure isolation tests pass |
| Frontend errors | Two raw `console.error(error)` calls replaced by fixed failure codes; component tests prove supplied message, stack and digest stay out of logs/UI |
| Synthetic demo | New E2E privacy test runs Maya with network connections forbidden; all external sources are example.org and raw evidence/child id stay out of telemetry |
| Preserved evaluation data | Existing synthetic declarations on the pinned page and v3/v4/v5 metadata are checked read-only; no tape, scorer, holdout or historical result changes |
| Frontend fixture data | Sentinel synthetic child id checked; existing production-surface tests keep fixture data out of ordinary production pages |
| Production dependency audit | `npm audit --omit=dev --json` reports two affected package groups: Next.js (critical) and PostCSS (high). This is a public-hosting blocker, not a clean dependency-security result |

The pattern scanner checks known credential formats; zero findings is the
recorded scan result, not a claim that every possible secret encoding can be
recognized. History scope is merged `main`, not a rewrite or modification of
other active branches. The holdout was not opened or evaluated for this audit.

Independent local probes confirm that an `act_` person id under `status`, and
a credential-shaped token under `reason_codes`, survive the current filter.
Existing Git/Postgres exception paths can also expose paths or raw error details.
The parallel audit's corrections to `telemetry.py` and `neatlogs_sink.py` fail
frozen `PROTECTED_RUNTIME_DRIFT` checks. Neither this PR nor the audit may refresh
protected hashes or rewrite historical evidence to bypass that failure.

The dependency finding is outside #59's credential/environment/log-redaction
acceptance scope and is not fixed by these logging changes. The audit includes
[Windows-hosted Next.js RCE](https://github.com/advisories/GHSA-p293-qw3h-jr36)
and [PostCSS file disclosure](https://github.com/advisories/GHSA-fxqj-rqcc-2cmp).
The lockfile pins Next.js 14.2.35; npm proposes a major-version upgrade. Do not
claim the Next.js server is ready for public deployment on the basis of this
audit. The canonical offline Maya artifact requires no Next.js server.

## Reproduce

```sh
uv run python scripts/secret_scan.py
uv run pytest tests/test_repo_hygiene.py tests/test_observability.py \
  tests/test_neatlogs_sink.py tests/test_runtime_tracing.py \
  tests/test_synthetic_demo_privacy.py -q
cd app/web
npm ci
npm test -- --run app/error-privacy.test.tsx
npm run typecheck
```

Backend audit suite: **29 passed**. Frontend privacy suite: **2 passed**;
frontend typecheck passed. Ordinary CI must pass before merging.
The full reset/demo chain is already covered in
[Maya instructions](maya-demo.md), and the database access boundary has existing
real-Postgres adversarial tests in `tests/test_rls.py`.

Do not enable generic provider auto-instrumentation that exports prompts or
completions. Use the committed SafeTelemetry/NeatLogs sink. Its allowed fields
are controlled codes, ids and counts, not a channel for arbitrary user values.
Synthetic judging artifacts may be shared; local credentials and real family
narratives may not. `.env`, runtime outputs and `.demo/` remain ignored.
