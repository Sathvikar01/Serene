# Final reconciliation and submission evidence audit — 18 October 2026

## Revision and evidence boundaries

Freshly fetched `main`: `d90c227d542ceaef7660c33e01d5d674b3901170`.
PR #114: `e0608222f5eab92ed17a8d8d4acd8066ab27bae8`.
PR #115: `e4586b4e41a0ec7d7374d58482efb7cd0f8da310`.
Both were OPEN/MERGEABLE when inspected. Neither was merged on GitHub.
PR #67 was CLOSED with no merge timestamp; its implementation remains DEV-only.
The integration uses a new isolated worktree; unrelated local edits were preserved.

Classifications apply to the precise claim, not an entire technology:

- **PROVEN**: reproducible repository implementation/evidence supports the bounded claim.
- **HISTORICAL**: a dated service/validation receipt; no fresh execution is implied.
- **DEV-ONLY**: evidence for an experimental revision outside product main.
- **SYNTHETIC**: fictional records, scripted I/O or assumed financial inputs.
- **UNVERIFIED**: evidence needed for the claim is absent or was not executed here.

A historical service receipt and a locally reproducible test are separate claims.
Passing a local adapter test does not refresh a hosted/provider/sponsor receipt.
No holdout, provider evaluation, rescore or modification of archived results is
part of this audit.

## Conflict analysis and reconciliation

Combining #114 then #115 produced one textual conflict in
`app/web/app/demo/maya/MayaDemoView.tsx`: #114 removes the repeated fictional
banner and uses `SurfaceLoading`; #115 updates the banner's approval wording
while replacing hardcoded success prose with canonical fields. Resolution keeps
the compact loader and all canonical summary/takeaway fields. A single fictional
description remains in the page introduction so removal of repeated banners does
not erase the synthetic boundary.

The following overlaps merged automatically and were reviewed semantically:

| File | Preserved intent |
| --- | --- |
| `app/web/app/layout.tsx` | #115 server-owned inline bootstrap; #114 server-provided demo flag and loading integration |
| `app/web/e2e/causal-twin.spec.ts` | #115 executes viewport cases without skips; #114 absent empty panel and selection before panel-position assertions |
| `app/web/e2e/maya-demo.spec.ts` | #115 canonical question/intervention/outcome/candidate comparisons; #114 opens disclosures and checks structured reason codes |
| `app/web/e2e/memory.spec.ts` | #114 disclosure interactions; #115 requires exactly one patch before viewport/status checks |

Canonical correction authority, tampered-memory rejection and historical Git
bytes are inherited unchanged from #115. Ask Serene, compact layouts, approval
controls, keyboard disclosures and the loading animation are inherited from #114.

Independent review found one inherited #114 defect: when the experiments
projection is unreadable and no question is pending, Today incorrectly says
“Nothing needs your attention” and hides the existing unreadable-decisions
warning. The minimal fix renders the warning even with zero known decisions;
a regression failed before the fix and passes afterward. Valid empty projections
retain the compact empty state. Maya browser checks now explicitly open Memory
history, require visible patch/rejection records and all six Dream stages, and
check the populated story's console. Deliberate missing-artifact non-2xx states
remain tested separately; page exceptions are captured throughout.

## Submission claim audit

| Important claim | Classification | Repository evidence and exact boundary |
| --- | --- | --- |
| Hermes proposal/admission boundary is implemented | PROVEN | `serene/adapters/hermes/`, `serene/investigation/`, runtime/transport tests and deterministic Inspect runtime task. Scripted wire tests do not prove provider availability. |
| Live Hermes/provider runs occurred | HISTORICAL | [Controlled DEV record](controlled-dev-1.md), archived Hermes before/after manifests, per-pair usage and verification receipts. Private raw states are not included in a fresh clone; a fresh provider execution is UNVERIFIED. |
| #67 improves measured evidence verification | DEV-ONLY | [36-pair archive](../eval/reports/archive/2026-10-12-controlled-dev-1/summary.json): 62/62 → 3/39 unsupported rejections, 0 → 22 verified captures. All 72 arms parked; no holdout/generalization or shipped-fix claim. |
| Postgres ledger, migrations, RLS and projections work locally | PROVEN | `tests/conftest.py`, Postgres ledger/projection/authorization tests and real-Postgres browser lanes. Auth/PostgREST/WS controls in those browser lanes are synthetic. |
| Hosted Supabase Auth/RLS/Realtime and connected UI were exercised | HISTORICAL | [12 October hosted proof](real-supabase-proof.md), [release audit](final-release-audit.md), opt-in preparer/browser/check scripts. Ignored credential-bearing logs are not public-clone evidence. Fresh integrated hosted validation is UNVERIFIED. |
| Git Memory Repo records reviewed commits and immutable revisions | PROVEN | `serene/memory/`, [publication contract](memory-publication.md), committer and projection tests; repository objects remain required for replay. Git/Postgres publication is not atomic. |
| Dream proposes, Critic reviews, one committer publishes; refused patch remains visible | PROVEN | Dream, Critic, committer tests and canonical Maya runner. Six stages and approved/refused changes exercise domain services with SYNTHETIC I/O; this is not autonomous live learning proof. |
| Corrected facts invalidate or review dependent learning | PROVEN | #115's five correction cases in `tests/test_memory_projection.py`: supersession, contradiction, refutation, context drift, overdue review; Memory/retrieval/projection/Twin agree without rewriting Git. |
| Causal Twin retains candidate/supported/refuted/superseded provenance | PROVEN | Twin builders/parsers/provenance tests and browser lanes. Unnamed endpoints remain listed rather than guessed; scoped N-of-1 support is not a general causal-effect estimate. |
| Inspect AI was used to execute invariant/core tasks | PROVEN | `eval/tasks/`, CI workflow, `scripts/inspect_gate.py`, core report runner. `mockllm/model` is deterministic/SYNTHETIC; exit zero from Inspect alone is insufficient, so gate/report must also pass. |
| Entire was genuinely used in development | HISTORICAL | [Sanitized native checkpoint/commit/session receipt](release-evidence.md). Two local records were retrievable in prior audits; Git trailers do not make native transcripts retrievable from a fresh clone. Complete coverage is UNVERIFIED/incomplete. |
| NeatLogs exports and diagnosis were real | HISTORICAL | [54 accepted suffix receipts](../eval/reports/archive/2026-10-12-controlled-dev-1/neatlogs-sessions.csv), verification receipt and [bounded diagnosis](release-evidence.md). No new live export or Telegram-specific tracing is claimed. |
| NeatLogs redaction and sink failure isolation are implemented | PROVEN | SafeTelemetry, sink/privacy tests; allow-list/HMAC/token filtering is not a universal PII detector. |
| cfo.ai scenario creation/readback occurred | HISTORICAL | [Saved scenario receipt](economics/cfo-evidence.json), request hashes and [readback](economics/cfo-readback.json). No fresh remote scenario or billing receipt. |
| $2.725256/family-month, 77.28% margin at $12, 524-day runway | SYNTHETIC | [Inputs](economics/inputs.json), [local report](economics/local-report.json), `scripts/economics_report.py --check`. Arithmetic is reproducible; every operating input is assumed, not measured spend, revenue or customers. |
| Maya 18/18, 63 events, fixed domain hash | SYNTHETIC | `scripts/demo_reset.py`, `scripts/maya_demo.py`, `verify_report` and Maya tests. Real domain services, scripted model/browser/Telegram I/O, fictional child. Reproducing the hash proves offline integration only. |
| Committed Maya screenshot and hero animation show current acceptance | HISTORICAL | `docs/images/maya-story.png`, `docs/videos/hero-landing.gif`/`.webm`. Presentation illustrations predate integration and cannot prove current canonical state, safety or external availability. |
| Public deployment, completed submission video, production/security/clinical readiness | UNVERIFIED | Repository explicitly makes no deployment, completed recording, clinical outcome or certification claim. An available hero animation is not the final submission recording. |
| Fresh integrated hosted/provider/NeatLogs/cfo.ai validation | UNVERIFIED | Not performed by this reconciliation; older evidence must keep its date and revision. |

## Wording corrected

- README's “final local presentation proves … LIVE” is dated to 12 October;
  it does not establish current #114/#115 hosted behavior.
- README's undated dependency/secret scan assertions now refer to revision-bound
  receipts rather than implying continuously fresh security evidence.
- Committed animation/screenshot captions are explicitly historical illustrations.
- The earlier documentation validation's unconnected-UI descriptions and counts
  are explicitly historical, preserving the receipt instead of rewriting history.
- Maya's single page introduction labels the story fictional while summaries
  continue to render canonical fields.
- README explicitly retains non-atomic publication, unnamed Twin endpoints and
  absence of fresh external validation.

The existing Maya guide is part of the hash-pinned reviewed synthetic corpus.
An initial explanatory annotation caused two corpus-integrity test failures;
the guide was restored byte-for-byte. Its historical screenshot is classified
here and in README instead. No manifest, scorer, protocol or archived result
was changed to accommodate documentation edits.

## Genuine limitations retained

Non-atomic Git/Postgres publication and projection recovery/backfill; required
retention of referenced Git objects; incomplete native Entire coverage; unnamed
Twin endpoints; metadata/digest lineage without a raw-evidence-content browser
endpoint; empty/filtered investigation-plan sufficiency; validity snapshot time
at ledger head; no fresh hosted/provider run; no public deployment or completed
submission recording; #67 CLOSED/unmerged and DEV-only; holdout not run and the
full research regression gate unpassed. A local synthetic demonstration and
historical sponsor usage do not remove these limitations.

## Fresh regression and manual receipts

All four required jobs passed on the clean integrated checkout at
`347de41b762f4583b43437650003f3222001fe34`:
[CI run 39143698879](https://github.com/Sathvikar01/Serene/actions/runs/39143698879).
The [sanitized machine-readable receipt](reconciliation-evidence.json) records
the input heads, environment, results, manual checks and failed/incomplete attempts.
Commands are the unchanged [CI workflow](../.github/workflows/ci.yml); run web
commands in `app/web`, Python commands at repository root.

| Requested gate | Complete fresh result |
| --- | --- |
| `npm run typecheck` | PASS |
| `npm test` | 287 passed, 44 files |
| `npm run build` | PASS; also a separate normal Windows production build without fixture routes |
| `npm run test:e2e` | 166 passed, zero skipped |
| `npm run test:e2e:approvals` | 2 passed; real disposable PostgreSQL, synthetic Auth/PostgREST and controlled WS delivery |
| `SERENE_E2E_SKIP_BUILD=1 npm run test:e2e:twin` | 1 passed; real PostgreSQL/RLS, same synthetic transport boundary |
| `uv run ruff check .` | PASS |
| `uv run ruff format --check .` | PASS; 303 files |
| `uv run mypy` | PASS; 108 source files |
| `uv run pytest` | 1,480 passed, two pre-existing Windows-specific pipe checks skipped on Linux, four dependency deprecation warnings |
| Inspect kernel/trust/runtime tasks + `scripts/inspect_gate.py` | 5/5 + 9/9 + 6/6 CORRECT; 20/20 total |
| Inspect core task + `eval/runners/core_scenarios_report.py` | 10/10 PASS |
| `uv run python scripts/ledger_selfcheck.py` | 25 events; valid chain, identical replay, tamper detected |
| `uv run python scripts/secret_scan.py` | Zero findings |
| Supplemental local env/synthetic/docs/economics checks | Zero env findings; 97 reviewed assets, zero synthetic findings; 383 references, zero docs failures; assumed economics reproduced |

Initial CI failed two corpus-integrity checks because this audit annotated the
hash-pinned Maya guide. Restoring its original bytes fixed the cause; the manifest
and tests were not changed. A local full pytest attempt was stopped under severe
memory pressure. A partial local web-unit run reported a timeout before it was
stopped. Neither attempt is counted as a pass; the complete clean CI results
above are the full-suite receipts. Today's unavailable-decision regression was
observed failing before its fix and both focused cases pass after the fix.

No browser test skip, assertion weakening, arbitrary sleep, production test
branch, evaluator/fixture/scorer change or holdout execution was introduced.

### Manual Maya review

Fresh reset and generation: 18/18, 63 events, canonical domain hash
`4000dac552cca6086d39e352795c2a2c79a0bedc69c823247a08c47173e12c7e`.
An ordinary production build, with fixture routes disabled and demo mode enabled,
served the real local artifact. No API interception or fixture route was used.

- Summary matches persisted question, intervention, approval, outcome and candidate
  alternatives. Accepted/rejected evidence remains available, including the retained
  `EXCERPT_NOT_ON_SOURCE` rejection. Earlier investigation checkpoint shows the
  parent question; the latest checkpoint returns to the completed investigation.
- Completed trial shows granted Telegram approval and the recorded outcome.
  Memory status/body and Git revision match canonical state; all six Dream stages
  and visible committed/refused patches were inspected. All 22 memory provenance
  links were followed with Enter and have one target in the viewport.
- Supported Twin opens full experiment/outcome/raw-evidence provenance with no
  missing nodes. The saved pre-trial view has no tested edge or experiment; the
  post-trial view restores the tested relationship. Candidate alternatives remain.
- At 1440, 768, 390 and 320 px, the Maya story has no horizontal overflow.
  Required approval details are initially open and blocked headers visible in the
  separate explicitly synthetic sample tour (two pending cards, one blocked card).
- A separate fresh Maya instance received an admitted hypothesis supersession:
  direct Memory, published Memory, retrieved belief and Twin learning validity
  agree on `NEEDS_REVIEW`; the edge is `SUPERSEDED`. Original Git bytes and revision
  `a811431e499a46cceb1ba8217c114c78e34e0c68` remain unchanged and the chain is valid.
  This is a direct canonical-state check, not an invented UI correction editor.
- Temporarily altered report memory was refused with HTTP 503. The browser cleared
  old summary/trial data and showed the unavailable state. The original artifact
  was restored byte-for-byte and reloaded successfully. This deliberate negative
  case emits the expected failed-resource diagnostic; populated/restored pages have
  zero console warnings/errors and no page exceptions or hydration errors.
- The same build with demo mode OFF shows no family data on Today, Investigations,
  Experiments, Memory or Twin. The canonical Maya state endpoint returns 404.
  Transient streamed duplicate DOM was allowed to settle to one target; no duplicate
  was selected away and no browser assertion was changed to accept duplicates.

Local screenshots/logs are retained separately under
`reconciliation-evidence-20261018/` beside this worktree. Committed older media
remain historical illustrations. The complete reset/regeneration journey also
passes in the 166-test CI browser suite.

## Changed files and delivery

Beyond the existing PR changes, the narrow fixes/evidence work touches
`app/web/components/today/TodayBrief.tsx`, its new regression test,
`app/web/e2e/maya-demo.spec.ts`, `app/web/app/demo/maya/page.tsx`, README,
`docs/final-docs-validation.md`, this audit and its JSON receipt. The Maya view
conflict resolution preserves both PR intents. Other overlap files require no
additional repair beyond the semantic merge described above. The hash-pinned
Maya guide, synthetic manifest, CI workflow and all evaluation artifacts have no
net changes from main.

One focused [integration PR #116](https://github.com/Sathvikar01/Serene/pull/116)
targets #114 and contains #115 plus the necessary reconciliations and evidence
corrections. A follow-up is required because of the Maya conflict and the hidden
unreadable-decision warning; it is not a presentation redesign.

Recommended order after human review: merge #115 to main; merge #116 into #114
to supply the verified reconciliation; then merge the reconciled #114 to main.
Git history must preserve the #115 ancestry (or be reconciled again if squashed),
and the final #114 head must pass required CI against updated main. No PR was
merged by this audit, and #67 remains closed/unmerged.
