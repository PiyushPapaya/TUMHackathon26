// Tests für die Modell- und Regionsauswahl im Marktvergleich. Start: node --test src/components/portfolio/compareModels.test.mjs
// Wie intents.test.mjs: Node-Test-Runner + vorhandenes "typescript" zum Übersetzen, keine neue Abhängigkeit.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import ts from "typescript";

const source = readFileSync(new URL("./compareModels.ts", import.meta.url), "utf8");
const { outputText } = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } });
const { comparableModels, groupModels, pickMarkets } = await import(`data:text/javascript,${encodeURIComponent(outputText)}`);

const s = (id, derivative, market) => ({ id, derivative, market, model_name: `BMW (${derivative})` });
const ALL = [
  s("F70-EU", "F70", "EU"),
  s("G60-EU", "G60", "EU"),
  s("G60-US", "G60", "US"),
  s("G68-CN", "G68", "CN"),
  s("G70-EU", "G70", "EU"),
  s("G70-US", "G70", "US"),
];

test("Nur Modelle mit mindestens zwei Regionen sind wählbar", () => {
  const models = comparableModels(ALL);
  assert.deepEqual(models.map((m) => m.derivative), ["G60", "G70"]);
  assert.deepEqual(models[0].markets, [{ market: "EU", scenarioId: "G60-EU" }, { market: "US", scenarioId: "G60-US" }]);
  assert.equal(models[0].label, "BMW (G60)");
});

test("Alle Modelle bleiben sichtbar, auch mit nur einer Region", () => {
  assert.deepEqual(groupModels(ALL).map((m) => [m.derivative, m.markets.length]), [["F70", 1], ["G60", 2], ["G68", 1], ["G70", 2]]);
});

test("Ohne Modell mit mehreren Regionen gibt es nichts zu vergleichen", () => {
  assert.deepEqual(comparableModels([s("F70-EU", "F70", "EU"), s("G60-US", "G60", "US")]), []);
});

test("Doppelte Region im selben Modell zählt nur einmal", () => {
  assert.deepEqual(comparableModels([s("G60-US", "G60", "US"), s("G60-US2", "G60", "US")]), []);
});

test("Regionen-Paar ist immer verschieden", () => {
  const markets = ["EU", "US", "CN"];
  assert.deepEqual(pickMarkets(markets, "", ""), ["EU", "US"]);
  assert.deepEqual(pickMarkets(markets, "CN", ""), ["CN", "EU"]);
  assert.deepEqual(pickMarkets(markets, "US", "US"), ["US", "EU"]);
  assert.deepEqual(pickMarkets(markets, "XX", "CN"), ["EU", "CN"]);
});
