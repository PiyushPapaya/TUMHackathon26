# Glossary

The words we use in the app and in the code, in plain language.

| Term | Meaning |
|---|---|
| **Scenario** | One vehicle in one market, for example G60-US (5 Series, USA). Defined by one JSON file in `config/scenarios/`. |
| **Evidence** | One single piece of input: a customer comment, a study answer, a web page, a NHTSA complaint. Each has a stable ID like `EV-G60-US-FB-G60-0292`. |
| **Finding** (code: *signal*) | Something customers keep saying, built from many pieces of evidence. Can be a complaint, an unmet need, something they love, a competitor advantage or a trend. |
| **Requirement** | What the successor must do, written from the customer's view, with a measurable success criterion. Built from one or more findings. |
| **Success criterion** | The test that decides whether a requirement is met. Contains a number, for example "within 5 seconds". |
| **Score** | 0-100. A weighted sum of six factors, discounted by evidence level. See [PRIORITIZATION.md](PRIORITIZATION.md). |
| **Weights** | How much each factor counts. Defaults are set by us, the PM can change them. |
| **Evidence level** | A, B, C or D. How well a requirement is backed. A = two BMW sources agree, D = mostly an assumption. |
| **Traffic light** | The evidence level as a color: green (A, B), yellow (C), red (D). |
| **Assumption** | Something that has to be true for a requirement to be right, but that the data does not prove. Always listed separately. |
| **Conflict** | Two customer groups disagree, for example BEV and ICE owners. Shown, not averaged. |
| **Already offered?** | Check against today's option list: is this a real gap, or does it exist as an option already? |
| **Challenge** | The PM asks the AI a critical question about a requirement. The answer must cite supporting and counter-evidence. |
| **Prompt lens** | "Ask in your own words". The AI turns a question into weights and topics, Python re-ranks. |
| **What-if** | A live preview of new weights. Saves nothing. |
| **Audit trail** | The log of every AI proposal and PM decision, with reason, before and after. |
| **Hash chain** | Each audit entry stores a fingerprint of the previous one. Changing an old entry breaks the chain, and the check turns red. |
| **Bundle / snapshot** | The finished pipeline output for one scenario, one JSON file. The backend loads it at start. |
| **Pipeline** | The offline process that turns raw data into a bundle: read, find, research, write, score. |
| **Demo mode** | `DEMO_MODUS=true`. The app uses cached AI answers and never calls the network. |
| **Grounding** | The share of cited IDs that really exist. Ours is 100 %. |
| **Next-gen bet** | A requirement aimed at the successor's world (2030), backed more by trends than by today's customers. Usually level D. |
| **Thin / cold-start scenario** | A scenario with little or no customer feedback, like G68-CN. Fewer proposals, clearly marked. |
