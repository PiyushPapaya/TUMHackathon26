# Using the cockpit

A walk through one real session: deciding what the next BMW 5 Series (G60) in the US should do better.
It takes about ten minutes. All screenshots are from the running app in demo mode.

To start the app locally, see the [README](../../README.md#try-it).

## 1. Pick a model and market

Open **Models** in the top menu, or use the dropdown in the top right. Every card shows how much
customer data is behind the scenario. That number matters: 3,610 comments give you a very
different list than 19.

![Models and markets](../images/models.jpg)

## 2. Read the ranked list

**Cockpit** shows the requirements for the successor, best first.

![Cockpit](../images/cockpit.png)

What you see per row:

- **Rank and score** (0-100). Higher means more customers affected, a bigger satisfaction gap and stronger proof.
- **Traffic light.** Green = proven (A or B), yellow = weak (C), red = assumption (D). The letter is next to it.
- **Status.** Everything starts as *Proposed*. Only you change that.
- **Small warning sign** if customer groups disagree on this topic.

Use the filters to narrow it down, for example *Evidence: weak* to see what still needs work.
Top right: the funnel (3,610 comments → 58 findings → 19 requirements) and the export buttons.

## 3. Ask in your own words

Open **Ask a prioritization question** and type what you care about, the way you would say it in a meeting:

> Families in the US who road-trip a lot. What should we fix first?

![Ask in your own words](../images/ask-in-your-words.png)

The tool shows how it understood you (which weights, which topics) and a preview of the new top 5.
Nothing changes yet. If it looks right, press **Apply & re-rank**. Your question is saved as the
reason in the audit trail, so later everyone can see *why* the ranking shifted.

Prefer to do it by hand? Open **Fine-tune weights** and move the sliders. The list previews live.
**Apply weights** saves it, **Reset to default** goes back.

![Weight sliders](../images/weights.png)

## 4. Open a requirement

Click any row. The left side tells you what the requirement is. The right side tells you why it is ranked there.

![Requirement detail](../images/requirement-score.png)

Read it top to bottom:

- **Title and success criterion.** Written from the customer's view, with a number you could test.
  "≥ 90 % of participants change the temperature within 5 seconds" is something an engineer can build against.
- **Why this priority.** Each factor as a bar. Open *Calculation details* to see the exact input.
  The last step shows the discount for weaker evidence.
- **Without future factor.** A toggle that shows the score if you ignore the 2030 trend assumption.

Scroll down for the evidence:

![Findings, already-offered check and assumptions](../images/requirement-evidence.png)

- **What customers say.** The findings behind it. Expand one to read the actual quotes, with country, drivetrain and source.
- **Already offered?** A check against today's option list. *"No, not offered today"* means it is a real gap.
  *"Only as an option"* might mean a packaging decision, not an engineering one.
- **Assumptions and open questions.** What has to be true for this requirement to be right. Read these before you approve.

## 5. Decide

The **PM decision** panel has four actions. All of them need a reason.

| Action | When to use it |
|---|---|
| **Approve** | You are convinced. It goes into the decision memo. |
| **Reject** | Not now, or not for this car. Say why, so the next person knows. |
| **Edit** | The idea is right but the wording or the criterion is off. Change title, description, criterion, effort, assumptions. |
| **Challenge** | You are not sure. Ask the AI a pointed question. |

A challenge looks like this:

![Challenge with AI answer](../images/challenge.png)

There are a few ready-made questions (*"Is this only a US issue?"*, *"What speaks against it?"*) or you
write your own. The answer always lists **supporting evidence** and **counter-evidence** as clickable IDs.
If there is no counter-evidence, it says "None cited" instead of making some up. The requirement is
marked *Challenged* until you approve or reject it.

## 6. Check the audit trail

**Audit trail** lists everything that happened, newest first: what the AI proposed, what you decided, and why.

![Audit trail](../images/audit-trail.png)

- The box at the top checks the whole chain. *Integrity verified* means no entry was changed afterwards.
- Click an entry to see the details on the right, including before and after values.
  A weight change reads like "customer pain 25 % → 23 %".
- Filter by who acted (PM, AI, system), by action, or search for a requirement or a reason.

## 7. See what you don't know

**Insights** (open `/insights` in the browser) has four tabs. Two are the most useful in a planning meeting:

| Evidence vs. assumption | What we do not know |
|---|---|
| ![Insights matrix](../images/insights-matrix.png) | ![Unknowns](../images/insights-unknowns.png) |

- **Evidence vs. assumption** splits requirements into "safe and urgent today" and "bets on the successor".
- **What we do not know** lists the weakly backed requirements, why they are weak, and the next study that would settle them.

## 8. Share the result

Back in the cockpit:

- **Export CSV** gives you the full list with scores, levels, criteria and status, ready for Excel.
- **Decision memo** gives you a Markdown summary: approved requirements (or the top 5 as a draft), with
  evidence, assumptions and a line confirming the audit trail is valid.

## Tips from our own testing

- Start with the traffic light filter set to *weak*. Those are the items people will ask about.
- Challenge your top 3 before approving them. It takes a minute and you will have the counter-arguments ready.
- Write reasons for the person who reads them in six months, not for yourself today.
- Compare markets (**Compare** in the menu). If a requirement is top 5 in the US and Europe, it is probably a platform topic.
