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

The execution record will be completed after all requested gates and the normal
production Maya browser review finish. Until then this document is an audit in
progress, not a passing integration certificate.
