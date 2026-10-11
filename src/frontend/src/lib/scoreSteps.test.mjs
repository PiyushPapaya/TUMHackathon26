// Tests: Der Satz "Ranked mainly because of ..." nennt dieselben Punkte wie das Score-Diagramm.
// Start: node --test src/lib/scoreSteps.test.mjs (Node-Test-Runner + vorhandenes "typescript", keine neue Abhängigkeit).
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import ts from "typescript";

const source = readFileSync(new URL("./scoreSteps.ts", import.meta.url), "utf8");
const { outputText } = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } });
const { chartFactorSteps, rationaleWithChartPoints } = await import(`data:text/javascript,${encodeURIComponent(outputText)}`);

const f = (contribution, weight) => ({ value: contribution / (weight * 100), weight, contribution, explanation: "" });
const BREAKDOWN = {
  customer_pain: f(25, 0.25), reach: f(4.3, 0.1), satisfaction_gap: f(12, 0.2),
  competitive_pressure: f(0, 0.15), future_relevance: f(1, 0.2), effort_inverse: f(6, 0.1),
};
const STALE = "Ranked mainly because of customer pain (30 points) and reach (9 points). Evidence level A: 25 mentions.";

test("Punkte im Satz kommen aus dem Diagramm, nicht aus dem gespeicherten Text", () => {
  const steps = chartFactorSteps(BREAKDOWN, undefined, false);
  assert.equal(
    rationaleWithChartPoints(STALE, steps),
    "Ranked mainly because of customer pain (25.0 pts) and satisfaction gap (12.0 pts). Evidence level A: 25 mentions.",
  );
});

test("Vorschau ohne Zukunftsfaktor: Satz nutzt die umgerechneten Balken", () => {
  const steps = chartFactorSteps(BREAKDOWN, undefined, true);
  assert.ok(!steps.some((s) => s.factor === "future_relevance"));
  // 25 / 0.8 = 31.25 und 12 / 0.8 = 15, genau wie die Balken im Diagramm.
  assert.match(rationaleWithChartPoints(STALE, steps), /customer pain \(31\.3 pts\) and satisfaction gap \(15\.0 pts\)\./);
});

test("Backend-Wasserfall hat Vorrang, Konfidenz-Schritt zählt nicht als Faktor", () => {
  const waterfall = [
    { factor: "reach", label: "Reach", value: 1, weight: 0.1, contribution: 10, sentence: "" },
    { factor: "customer_pain", label: "Pain", value: 0.2, weight: 0.25, contribution: 5, sentence: "" },
    { factor: "confidence", label: "A", value: 1, weight: null, contribution: 50, sentence: "" },
  ];
  const steps = chartFactorSteps(BREAKDOWN, waterfall, false);
  assert.match(rationaleWithChartPoints(STALE, steps), /reach \(10\.0 pts\) and customer pain \(5\.0 pts\)/);
});

test("Text ohne Punkte-Satz bleibt unverändert", () => {
  const steps = chartFactorSteps(BREAKDOWN, undefined, false);
  assert.equal(rationaleWithChartPoints("Edited by PM.", steps), "Edited by PM.");
});
