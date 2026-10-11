// Tests: Segment-Konflikte (A1) lesbar machen: "BEVE"/"A" sind Rohcodes aus den BMW-Daten, die eine PM nicht versteht.
// Start: node --test src/lib/segmentConflicts.test.mjs (Node-Test-Runner + vorhandenes "typescript", keine neue Abhängigkeit).
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import ts from "typescript";

const source = readFileSync(new URL("./segmentConflicts.ts", import.meta.url), "utf8");
const { outputText } = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } });
const { describeSegmentConflict } = await import(`data:text/javascript,${encodeURIComponent(outputText)}`);

// Echte Form aus data/processed/G60-US/requirements.json
const ENGINE = {
  dimension: "engine", segment_a: "BEVE", segment_b: "PHEV", a_count: 34, b_count: 10,
  statement: "Electric Range: BEVE mostly criticises (34); PHEV mostly praises (10).",
  evidence_ids: ["EV-1", "EV-2"],
};

test("Antrieb: Rohcodes werden zu Klartext, Thema aus dem Satz", () => {
  const view = describeSegmentConflict(ENGINE);
  assert.equal(view.topic, "Electric Range");
  assert.equal(view.dimensionLabel, "Drive type");
  assert.deepEqual(view.critical, { label: "Electric (BEV)", count: 34 });
  assert.deepEqual(view.positive, { label: "Plug-in hybrid", count: 10 });
});

test("Quelle: anonymisierte Kanäle A/B werden als Feedback-Kanal benannt", () => {
  const view = describeSegmentConflict({ ...ENGINE, dimension: "source", segment_a: "A", segment_b: "B" });
  assert.equal(view.dimensionLabel, "Feedback channel");
  assert.equal(view.critical.label, "Channel A");
  assert.equal(view.positive.label, "Channel B");
});

test("Land: Ländercode wird zum Namen", () => {
  const view = describeSegmentConflict({ ...ENGINE, dimension: "country", segment_a: "US", segment_b: "DE" });
  assert.equal(view.critical.label, "United States");
  assert.equal(view.positive.label, "Germany");
});

test("Studie gegen Feedback: Studie hat keine Kommentarzahl (b_count=1 ist nur ein Platzhalter)", () => {
  const view = describeSegmentConflict({
    dimension: "study_vs_feedback", segment_a: "feedback", segment_b: "study", a_count: 21, b_count: 1,
    statement: "Cushioning / damping vehicle: 21 critical comments, while the study reports satisfaction.",
  });
  assert.equal(view.topic, "Cushioning / damping vehicle");
  assert.deepEqual(view.critical, { label: "Customer feedback", count: 21 });
  assert.deepEqual(view.positive, { label: "Customer study", count: null });
});

test("unbekannte Codes und fehlende Felder brechen nichts", () => {
  const view = describeSegmentConflict({ dimension: "web", statement: "no colon here" });
  assert.equal(view.topic, null);
  assert.equal(view.critical.label, "Group A");
  assert.equal(view.critical.count, null);
});

test("Befund gegen Befund (dimension 'signal', aus core/views.py): kein Segmentvergleich", () => {
  const view = describeSegmentConflict({
    dimension: "signal", signal_ids: ["SIG-1", "SIG-2"],
    statement: '"Range feels limited" contradicts "Range is better than quoted"',
  });
  assert.equal(view.dimensionLabel, "Opposing findings");
  assert.equal(view.isSegmentComparison, false);
  assert.equal(describeSegmentConflict(ENGINE).isSegmentComparison, true);
});
