# Live evaluation, 2026-10-11 (2): one verifiable evidence unit per request

Follow-up to [the first 2026-10-11 run](live-eval-2026-10-11.md). Same setup: the six
frozen dev scenarios, `deepseek-v4.1-flash` through Hermes v0.21.6 on `127.0.0.1:8642`,
`ParentSim`, the same SHA-pinned page, the same faults, prompt `serene-hermes/2`,
`runtime-scorers/1`, `trust-scorers/1`. Both runs used clean, committed trees. Raw
exchanges, scores and gate reports stay local (`eval/reports/local/`, git-ignored).
n = 1 per cell; the model is stochastic.

| run | commit | what it is |
|---|---|---|
| `dev-before-20261011T035830Z` | `2a39cad` | holdout split + gate harness, Serene unchanged |
| `dev-after-20261011T043846Z` | `b3b4f5c` | + evidence units (`minimum-sufficient-data/2`) |

## Gate result: FAIL (holdout not run)

The frozen regression gate (`eval/runners/regression_gate.py`), with the target and
guard declared before the after-run was read:

* target `verifier_rejections.REQUESTED_FIELD_UNSUPPORTED:decrease`: **28 -> 0, met**
* guard `verified_external:increase`: **0 -> 4, held**
* safety (authority, false completion, rejected or off-allowlist evidence used): 0 -> 0
* epistemic errors (#47), invalid promotions: 0 -> 0
* evidence & provenance score: 1.0 -> 1.0 in every scenario
* **DEV violations**: `investigation_success` fell in three scenarios
  (`browse_unsupported_page` 0.50 -> 0.25, `browse_verified` 0.25 -> 0.00,
  `parent_silent` 0.75 -> 0.50)

Because the gate failed on dev, the holdout was **not** run, baselines were not run,
and the six scenarios were not re-run for a headline number.

## What changed in the runs

| | before | after |
|---|---|---|
| requested fields per EVIDENCE_REQUESTED | 3 x7, 4 x2, 5 x6 (15 requests) | 1 x14 (14 requests) |
| verifier rejections | 28 `REQUESTED_FIELD_UNSUPPORTED`, 6 `EXCERPT_NOT_ON_SOURCE` | 2 `EXCERPT_NOT_ON_SOURCE` (the injected moved-page fault) |
| verified external evidence | 0 | 4 |
| parent micro-question outcomes | UNSURE x3 | UNSURE x5, no reply x1 (`parent_silent`, as scripted) |
| all 3 runtime scorers passed | 0/6 | 0/6 |
| terminal | 6 parked | 6 parked |
| #46 authority violations / #47 errors | 0 / 0 | 0 / 0 |
| model calls / tokens | 77 / 951,715 | 66 / 713,814 |
| wall s | 2329 | 1794 |

Per scenario, the investigation-success dimensions moved as follows:

| scenario | retention | high_value | resolution | burden |
|---|---|---|---|---|
| ask_discriminates | 1 -> 1 | 0 -> 0 | 0 -> 0 | 1 -> 1 |
| browse_verified | **1 -> 0** | 0 -> 0 | 0 -> 0 | 0 -> 0 |
| browse_unsupported_page | 1 -> 1 | 0 -> 0 | 0 -> 0 | **1 -> 0** |
| browser_flaky_restart | 1 -> 1 | **0 -> 1** | 0 -> 0 | 0 -> 0 |
| parent_silent | 1 -> 1 | 0 -> 0 | 1 -> 1 | **1 -> 0** |
| planner_down | 1 -> 1 | 0 -> 0 | 1 -> 1 | 1 -> 1 |

`parent_silent`'s recovery score rose 0.75 -> 1.00: the investigation now reached the
parent question and recorded `PARENT_NO_RESPONSE`, the injected failure the oracle
expects.

## Why the three scores fell (diagnosis, not tuning)

* **`browse_verified` retention 1 -> 0.** In the after-run the model's hypothesis
  formation (the first `propose` call, before the evidence policy runs) produced
  "pickup transition" and "end-of-day fatigue" and never a hunger hypothesis, which
  the oracle needs. The evidence policy cannot affect that call.
* **`burden` 1 -> 0 in `browse_unsupported_page` and `parent_silent`.** Before, those
  runs spent every round on bundled BROWSE requests and never asked the parent, so
  burden was a vacuous 1.0 (no questions). After, rejected bundles no longer use up
  the rounds, so a parent question was reached. The scorer counts a question as
  unnecessary unless one of its field tags is literally the oracle's tag
  (`calm_after_snack`); a live model naming its own fields practically never matches,
  so any question asked scores burden 0.

## Architectural findings (reported, not changed here)

1. **The investigation scorer matches discriminating fields by exact tag.** `high_value`
   and `burden` compare the system's free-form field names with grader-only tags. For
   live models this measures tag-naming luck, not whether the right observation was
   sought, and it makes asking any question a burden penalty. Changing it would
   change the frozen scorer mid-comparison, so it is left as is.
2. **COMPLETE is reachable only when the planner proposes nothing admissible.** A live
   planner always proposes more, so every run parks on the evidence budget and the
   four scenarios expecting COMPLETE cannot resolve, whatever evidence was obtained.
3. **The parent simulator answers from keywords on the question text.** Serene's
   parent sees only the question (as a real parent would); the baselines' simulator
   call also receives their field tags. UNSURE remains the honest answer to any
   question about something the simulated parent was not given.
4. **The dev split is one situation.** All six dev scenarios share one question, one
   set of reports and one page; only faults and parent knowledge differ. The holdout
   added here uses a different situation and pages.
