# How the ranking works

If a PM can't explain why item 3 is above item 4, they can't defend the list in a meeting.
So the score in ReSpec is not an AI opinion. It is a short formula in
[`scoring.py`](../../src/backend/requirements_engine/scoring.py) that you can redo with a calculator.

## The formula

```
score = (sum of factor × weight × 100) × evidence confidence
```

Six factors, each between 0 and 1. The weights add up to 1, so the raw score is between 0 and 100.
Then the score is discounted depending on how well the requirement is backed.

## The six factors

| Factor | Default weight | The question behind it | How it is computed |
|---|---|---|---|
| Customer pain | 25 % | How much does it bother people? | Defects and usability problems count more than wishes |
| Reach | 20 % | How many people does it affect? | Mentions (square-root scale) × the market's share of 2030 sales volume |
| Satisfaction gap | 20 % | How unhappy are customers in the study? | Share of unsatisfied customers on the matching study question |
| Competitive pressure | 15 % | Do competitors already do it better? | Only trusted web sources that show a competitor advantage count |
| Future relevance | 10 % | Will it matter more in 3-5 years? | Trends and market growth. This is an assumption, and labeled as one |
| Low effort | 10 % | Is it cheap to do? | Effort estimate: S = 1.0, M = 0.6, L = 0.2 |

The weights are a judgment call. These defaults are our best guess for a premium car in 2030.
That is exactly why the PM can change them, either with sliders or by asking a question in plain
English (see [PM_GUIDE.md](PM_GUIDE.md)). Every applied change is logged with a reason.

## Evidence confidence

A requirement backed by thousands of comments and a study should beat a hunch with the same raw
score. So the raw score is multiplied by a confidence factor:

| Level | Traffic light | Factor | Rule (from [`evidence_level.py`](../../src/backend/requirements_engine/evidence_level.py)) |
|---|---|---|---|
| A | green, "Strong" | 1.00 | 15+ mentions and confirmed by both BMW sources (feedback **and** study) |
| B | green, "Moderate" | 0.85 | 15+ mentions from one source, or confirmed by a second source type (web counts here) |
| C | yellow, "Weak" | 0.70 | Fewer than 15 mentions and no confirmation, or only web sources |
| D | red, "Assumption" | 0.50 | A bet on the next generation with little direct customer data |

Two rules we argued about:

- **Many mentions from one source never give A.** One source can be wrong in a systematic way.
- **Web can lift a requirement to B, never to A.** During testing almost every topic had some web hit,
  and many of them barely touched the topic. A competitor's trunk volume is not evidence for a door lock problem.
  BMW's own data counts more than the internet.

## A real example

Rank 1 for the BMW 5 Series (G60) in the US, with default weights:
*"HVAC controls and vents are obvious and operable quickly, and interior storage is functionally usable"*

| Factor | Value | × Weight | = Points | Why |
|---|---|---|---|---|
| Customer pain | 1.00 | 0.25 | 25.0 | Mostly "difficult to use" complaints, 25 mentions |
| Reach | 0.215 | 0.20 | 4.3 | 25 of at most 543 mentions; US is 25 % of 2030 volume |
| Satisfaction gap | 0.60 | 0.20 | 12.0 | 15 % unsatisfied with heater/AC controls in the study |
| Competitive pressure | 0.00 | 0.15 | 0.0 | No trusted source shows a competitor advantage |
| Future relevance | 0.103 | 0.10 | 1.0 | No trend behind it; market growth +2.6 % |
| Low effort | 0.60 | 0.10 | 6.0 | Effort estimate M |
| **Raw score** | | | **48.3** | |
| × Evidence level A | | | × 1.00 | Feedback and study agree |
| **Final score** | | | **48.3** | |

The cockpit shows exactly this as a waterfall on the requirement page, with a "calculation details"
link under each bar.

## How stable is the ranking?

If the list flips completely when someone nudges a weight, it is not worth much. So for every
scenario we run 200 simulations where each weight moves randomly by up to ±20 %, and count how
much of the top 5 survives. For G60-US it is 91 %, and the #1 stays #1 in all 200 runs.
Each requirement also shows its own range ("rank 2-4 in 200 runs"). See
[EVALUATION.md](../EVALUATION.md) for all scenarios.

## Why not let the AI rank?

We tried to think of a reason and couldn't find a good one. An LLM ranking changes between runs,
can't tell you why item 3 beats item 4, and can't be audited. The AI is good at reading thousands
of comments and writing clear requirements. Adding up six numbers is a job for plain code.
