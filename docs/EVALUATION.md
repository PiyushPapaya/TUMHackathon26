# Evaluation

A tool that ranks requirements for a car that ships in 2030 has to earn trust. "The AI looked
good in the demo" is not enough. So we measured what we could, and we wrote down what we could not.

## What we measure

| Check | Question it answers | Target |
|---|---|---|
| Grounding (findings) | Does every evidence ID a finding cites actually exist? | 100 % |
| Grounding (requirements) | Does every finding ID a requirement cites actually exist? | 100 % |
| Verbatim quotes | Is every quoted customer comment word for word in the original Excel file? | 100 % |
| Finding fidelity | Does the quoted comment really support what the finding says? Checked by people | ≥ 80 % |
| Coverage | How many in-scope comments ended up in at least one finding? | for orientation |
| Number in criterion | Does the acceptance criterion contain a number? | ≥ 80 % |
| Rank stability | If every weight moves by up to ±20 %, how much of the top 5 survives? (200 runs) | ≥ 80 % |

## Results for all six scenarios

| Scenario | Evidence → findings → requirements | Grounding | Verbatim | Coverage | Number in criterion | Top 5 stable |
|---|---|---|---|---|---|---|
| G60-US (5 Series, US) | 3,867 → 58 → 19 | 100 % | 100 % | 41.8 % | 100 % | 91 % |
| F70-EU (1 Series, EU) | 1,570 → 56 → 20 | 100 % | 100 % | 72.5 % | 100 % | 87 % |
| G70-US (7 Series, US) | 4,017 → 58 → 15 | 100 % | 100 % | 40.3 % | 100 % | 100 % |
| G60-EU (5 Series, EU) | 253 → 19 → 9 | 100 % | 100 % | 50.5 % | 100 % | 99 % |
| G70-EU (7 Series, EU) | 154 → 11 → 4 | 100 % | n/a | 0 % | 100 % | 100 % |
| G68-CN (5 Series LWB, China) | 177 → 5 → 5 | 100 % | n/a | n/a | 100 % | 100 % |

"Grounding" combines both grounding checks; both are 100 % everywhere.
Finding fidelity was measured for G60-US: **88 %** (44 of 50 pairs).

The per-scenario reports are generated, not written by hand:
[`tests/eval/REPORT.md`](../tests/eval/REPORT.md) (G60-US with fidelity) and
`tests/eval/REPORT-<scenario>.md` for the rest.

## How finding fidelity was measured

We drew 50 random pairs of (finding, quoted comment) with seed 42. For each pair the question was:
*does this comment support what the finding says?*

We are open about how it went. Claude suggested yes or no with a short reason for each pair.
Aditya went through all 50 and confirmed or corrected them. A second round, with Lasse checking
all 50 lines, also came out at 88 %, with partly different "no" cases. So the number is not
just the AI grading itself, but it is not a blind human label either.

## Limits

- **50 pairs is small.** Read 88 % as "roughly nine in ten", not as a precise figure.
- **Anchoring.** People reviewing AI suggestions tend to agree with them. A blind second label would be the next step.
- **Grounding says the source exists, not that the conclusion is right.** That is what fidelity is for.
- **"Number in criterion" is a syntax check.** It does not prove the number makes sense.
- **Coverage below 100 % is on purpose.** Topics without a BMW category and groups under 5 mentions are dropped.
- **Thin scenarios are thin.** G68-CN has no customer comments at all, G70-EU only 19. Their requirements rest on
  the study. We show that instead of padding the list.
- **Weights are a judgment call.** The defaults are our best guess. That is why the PM can change them, and why
  rank stability is measured.

## What else we checked

- Python test suite: `python -m pytest -q` (475 tests on Oct 11, including the cases below).
- `scripts/verify_stack.py`: loads all six scenarios through the API, runs PM actions, exports
  three formats, checks the audit chain and a full restart replay. Uses a temporary audit DB.
- `scripts/check_bundles.py`: rule checks on every snapshot in `data/processed/`.
- Frontend: lint, production build and the JavaScript unit tests.

Edge cases we found and fixed along the way, each with a regression test:

- A reason made of only spaces was accepted. Input is now trimmed first.
- A failed audit write could already change the PM state. State now changes only after the audit entry is stored.
- Two parallel writers could get the same predecessor hash. The write transaction now locks before reading.
- A missing pipeline step could pull in synthetic data from another scenario. It now fails loudly.
- Very large weights could overflow during normalization. They are scaled first.
- Missing benchmark data showed up as "0 complaints". It now shows as missing.

## Run it yourself

```bash
python -m pytest -q
python scripts/verify_stack.py
python scripts/check_bundles.py
python tests/eval/run_eval.py all       # needs the raw BMW files for the verbatim check
```
