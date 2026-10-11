// Tests: Das "!" in der Liste zeigt nur Widersprüche, die auch die Detailseite zeigt (beide Seiten zitiert).
// Start: node --test src/lib/conflicts.test.mjs (Node-Test-Runner + vorhandenes "typescript", keine neue Abhängigkeit).
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import ts from "typescript";

const source = readFileSync(new URL("./conflicts.ts", import.meta.url), "utf8");
const { outputText } = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } });
const { conflictTitlesFor } = await import(`data:text/javascript,${encodeURIComponent(outputText)}`);

const sig = (id, title, conflicts_with = []) => ({ id, title, conflicts_with });
const SIGNALS = new Map([
  ["A", sig("A", "Range feels limited", ["B"])],
  ["B", sig("B", "Range is better than quoted", ["A"])],
  ["C", sig("C", "Interior feels luxurious", ["D"])],
  ["D", sig("D", "Hands free trunk fails", ["C"])],
]);

test("beide Seiten zitiert: Widerspruch wird einmal gezeigt", () => {
  assert.deepEqual(conflictTitlesFor(["A", "B"], SIGNALS), ["Range feels limited ↔ Range is better than quoted"]);
});

test("Gegenseite nicht zitiert: kein Widerspruch (wie auf der Detailseite)", () => {
  assert.deepEqual(conflictTitlesFor(["D"], SIGNALS), []);
});

test("unbekannte IDs brechen nichts", () => {
  assert.deepEqual(conflictTitlesFor(["X"], SIGNALS), []);
});
