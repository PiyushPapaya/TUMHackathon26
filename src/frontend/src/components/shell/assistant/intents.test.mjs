// Tests für den Regel-Router des Assistenten. Start: node --test src/components/shell/assistant/intents.test.mjs
// Warum ohne Test-Framework: Node hat einen eingebauten Test-Runner, und "typescript" ist schon installiert.
// So kommt keine neue Abhängigkeit dazu. intents.ts hat nur Typ-Importe, darum reicht reines Übersetzen.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import ts from "typescript";

const source = readFileSync(new URL("./intents.ts", import.meta.url), "utf8");
const { outputText } = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } });
const { matchScenario, routeQuestion } = await import(`data:text/javascript,${encodeURIComponent(outputText)}`);

const scenarios = [
  { id: "G60-US", derivative: "G60", market: "US", model_name: "5 Series" },
  { id: "G60-EU", derivative: "G60", market: "EU", model_name: "5 Series" },
  { id: "G70-US", derivative: "G70", market: "US", model_name: "7 Series" },
];
const route = (text) => routeQuestion(text, { scenarioId: "G60-US", scenarios });

test("Stichwörter in längeren Wörtern lösen keine feste Antwort aus", () => {
  // "requi-red", "p-rot-ection", "sha-red", "s-top", "list-en" waren früher Treffer.
  for (const text of [
    "What features are required for families?",
    "Is battery protection important?",
    "Which complaints have customers shared most?",
    "Should we stop offering the sunroof?",
    "Do we listen to rear-seat passengers?",
  ]) {
    assert.equal(route(text).kind, "ask", text);
  }
});

test("Ganze Stichwörter und Mehrzahl treffen weiterhin", () => {
  assert.match(route("What does red mean?").text, /traffic light/);
  assert.equal(route("What should we build first?").kind, "top");
  assert.equal(route("What are our priorities?").kind, "top");
  assert.match(route("Show me the trends").navigate, /^\/insights/);
  assert.match(route("Explain the weights").text, /six factors/);
  assert.match(route("Where are the biggest opportunities?").navigate, /^\/insights/);
});

test("'users' wird nicht als US-Markt gelesen", () => {
  assert.equal(matchScenario(" 5 series for users in europe ", scenarios)?.id, "G60-EU");
  assert.equal(matchScenario(" 7 series us ", scenarios)?.id, "G70-US");
});
