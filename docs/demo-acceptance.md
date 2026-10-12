# Final demo acceptance checklist (#62)

**Release status: BLOCKED.** The canonical synthetic Maya domain demo passes;
the broader submission claims below are not all complete. A checked item records
a maintainer-reviewed result against its linked evidence. These checkmarks are
not automatic certification of third-party services, causal attribution or PII safety.

## Run using only this checklist

Prerequisites: full Git clone, Git, uv and Python 3.11–3.13. From the repository root:

```sh
uv sync --locked --all-extras --group dev
uv run python scripts/demo_reset.py
uv run python scripts/demo_reset.py
uv run pytest -q tests/test_demo_reset.py tests/test_maya_demo.py
uv run python scripts/maya_demo.py
uv run python -m scripts.demo_release
```

Open `.demo/maya/report.html`; inspect the numbered PASS rows, Twin, Dream
rejection and ledger. Retain `.demo/maya/report.json`. Expected canonical report
SHA-256: `3752477f9a66d039ba6002c72cfe9dc2e03c8e1332ccf0fe3ab728df6db9dbb9`.
The reset baseline hash is `41836ad96c19ec844870b7e185bd8ad548ad3beab90318350e07c93b15488681`.
The focused tests compare full reset snapshots and two independent domain runs.

The release command must currently exit **1**, listing the unchecked items,
and leave **no** `.demo/maya/judge-demo.zip`. That is a passing release-block test,
not a passing submission. It reuses the existing report verifier and refuses
missing/duplicate item IDs, missing evidence links, broken local references,
invalid ledger/order/seed and linked output targets. It withdraws an old bundle
before checking. Only when every item is reviewed and checked does it create a
deterministic ZIP containing the verified JSON, regenerated HTML, README and
checklist. It does not run or score an evaluation, contact a provider, or use a DB.
There is no force/skip option. The raw report remains available for rehearsal.

## Canonical domain beats

All inputs are synthetic. External Telegram/model/page I/O is scripted; real
channel, runtime, browser, verifier, policy, experiment, Dream and memory services
execute. These checks do not attest live network availability. Match each M-number
to its same-numbered report row and inspect the JSON events at the listed sequences.

- [x] **M01**: Telegram input enters the real channel; raw/structured pairs at 1–6, parent reply 17 and outcome reports 43–46. Evidence: [channel E2E](../tests/test_maya_demo.py).
- [x] **M02**: Investigation opens at event 7 under the authenticated synthetic parent. Evidence: [fixture](../serene/demo/maya.py).
- [x] **M03**: Fatigue, hunger and transition difficulty are competing hypotheses at 11–13. Evidence: [hypothesis test](../tests/test_maya_demo.py).
- [x] **M04**: Missing snack/pickup evidence is explicitly requested at 15, 21 and 29. Evidence: [report verifier](../serene/demo/report.py).
- [x] **M05**: Parent sees YES/NO/UNSURE and answers NO on the exact interaction, event 17. Evidence: [demo path](maya-demo.md#exact-path).
- [x] **M06**: Bounded browser acquisition records captures at 24 and 31. Evidence: [fixture](../serene/demo/maya.py).
- [x] **M07**: Exactly one injected TRANSIENT failure at 23 has attempt 1 and retryable=true. Evidence: [failure assertions](../serene/demo/report.py).
- [x] **M08**: RETRY_SCHEDULED leads to capture 24 for the same request, after failure 23. Evidence: [recovery assertions](../serene/demo/report.py).
- [x] **M09**: Independent verifier rejects unsuitable evidence at 26 with EXCERPT_NOT_ON_SOURCE. Evidence: [verification assertions](../serene/demo/report.py).
- [x] **M10**: A new request 29 obtains admissible evidence at 31, VERIFIED at 33 with all six checks; earlier rejection is retained. Evidence: [report verifier](../serene/demo/report.py).
- [x] **M11**: Reversible five-minute heads-up trial is proposed at 35, code-classified GREEN at 36. Evidence: [experiment path](maya-demo.md#exact-path).
- [x] **M12**: Exact parent approval at 39 precedes start 40 and outcome; no forged or automatic approval. Evidence: [order assertions](../serene/demo/report.py).
- [x] **M13**: Two pickup reports precede parent outcome 47 and experiment completion 48. Evidence: [fixture](../serene/demo/maya.py).
- [x] **M14**: Promotion Gate grants adjacent 3→4 at 49 and 4→5 at 50; scoped learning 51 retains provenance/review metadata. Evidence: [promotion assertions](../serene/demo/report.py).
- [x] **M15**: Dream records all six stages in order, events 52–56 and 59. Evidence: [Dream assertions](../serene/demo/report.py).
- [x] **M16**: Critic accepts one scoped patch and sole Memory Committer writes learnings/maya-pickup.md, event 61; inspect memory content/Git receipt in JSON. Evidence: [full-chain test](../tests/test_maya_demo.py).
- [x] **M17**: Universal single-observation patch is rejected at 63, INSUFFICIENT_EVIDENCE:OBSERVATION_BELOW_PATTERN; rejected file is absent. Evidence: [rejection assertions](../serene/demo/report.py).
- [x] **M18**: Twin transition edge is SUPPORTED level 5; fatigue/hunger remain CANDIDATE level 3. It is scoped synthetic support, not a clinical causal effect. Evidence: [Twin assertions](../serene/demo/report.py).

## Evidence, integration and submission gates

Items marked PASS below have committed evidence. Recheck CI against the final PR
head, and replace recording/public-build placeholders with real links before
checking them. Do not mark a limitation complete merely because it is documented.

- [x] **RESET**: Reset twice yields identical entire demo baseline, then the Maya run succeeds; no production DB access or manual editing. Evidence: [reset tests](../tests/test_demo_reset.py).
- [x] **PRIVACY**: Secret/history scan, env coverage, redaction and synthetic-data audit pass; metadata excludes raw narratives/errors. Representative tests are bounded, not universal PII certification. Evidence: [audited limits and commands](privacy.md#5-operational-audit-59).
- [x] **CI**: Backend, frontend, deterministic policy, lint/types, migrations/RLS and Inspect safety gates are required on main; final exact PR must be green. Evidence: [required checks](setup.md#5-merge-gates-58).
- [x] **NEATLOGS**: Demonstrate preserved controlled DEV session IDs and accepted export receipts for all 54 live suffixes, with redaction boundary disclosed. Offline Maya sends no live export. Evidence: [session index](../eval/reports/archive/2026-10-12-controlled-dev-1/neatlogs-sessions.csv).
- [x] **EVAL**: Present frozen methodology, final conditional DEV PASS, complete paired rows, safety/cost limits and honest parked outcomes; no holdout/superiority claim. Evidence: [controlled report](controlled-dev-1.md).
- [ ] **IMPROVEMENT**: BLOCKED — #53 needs full regression acceptance including holdout; eligibility alone is insufficient. No completed before→after success story. Evidence: [assessment](https://github.com/Sathvikar01/morrow/issues/53#issuecomment-6115724807).
- [ ] **ENTIRE**: BLOCKED — genuine ordered/retrievable native checkpoint coverage is incomplete; a Git milestone reference index cannot substitute. Do not resume #54 here. Evidence: [audited status](architecture.md#observability-economics-and-development-provenance).
- [x] **CFO**: Present actual cfo.ai Scenario/readback, assumed $2.725256/family-month and 77.28% margin at assumed $12 revenue; cost never grants safety/quality/approval authority. Evidence: [acceptance audit](economics/acceptance-audit.json).
- [x] **README**: Setup/reset/exact demo path, architecture, baseline/evaluation results, NeatLogs, Entire limitation and cfo.ai assumptions have evidence links. Fresh clone recipe succeeds. Evidence: [README](../README.md).
- [ ] **PUBLIC_BUILD**: BLOCKED — no verified public build URL or clean dependency/security review is recorded; last audit's Next/PostCSS advisories remain a separate hosting blocker. Evidence: [disclosed hosting limit](../README.md#verification-and-optional-integrations).
- [ ] **RECORDING**: BLOCKED — capture and review a full demo recording from reset through all 18 beats; attach an accessible artifact and verify synthetic-only frames. Evidence: [exact recording path](maya-demo.md#exact-path).
- [ ] **BACKUP**: BLOCKED — save and play an independently checked backup recording/artifact; record its actual location/hash. Evidence: [reproducible evidence format](maya-demo.md#reproducibility-and-judging).
- [ ] **SUBMISSION**: BLOCKED — verify final submission text, public evidence links and limitations against this checklist; attach the submitted receipt. Evidence: [claim limits](../README.md#documentation-and-current-limits).

## Recheck and signoff

```sh
uv run python scripts/docs_check.py --github docs/demo-acceptance.md
uv run pytest -q tests/test_demo_release.py
uv run python scripts/secret_scan.py --history
uv run python scripts/env_audit.py
uv run python scripts/synthetic_audit.py
uv run python scripts/economics_report.py --check
```

For a recording: show the reset command, run Maya, open the report, walk the
ordered rows, inspect rejection/recovery, approval, accepted/rejected Dream
patches and Twin, then show preserved NeatLogs/evaluation/cfo evidence and state
the open Entire/improvement limitations. Never replace real evidence with a staged
success receipt. Screenshot/recording paths are local ignored artifacts until
explicitly attached; their existence is not assumed by this checklist.

The checklist implementation can be complete while the release is blocked.
Passing CI tests the gate's refusal and fixture integrity; it does not waive
unchecked submission requirements. A maintainer must review and update the
evidence/checkmarks in a normal checked PR before a release bundle can be built.

