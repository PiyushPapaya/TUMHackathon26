// Das Backend liefert deutsche Quadranten-Namen. Die Oberfläche ist englisch, darum übersetzen wir hier an einer Stelle.
export const QUADRANT_EN: Record<string, string> = {
  "Sicher & dringend": "Safe and urgent",
  "Belegte Zukunftswette": "Evidenced future bet",
  "Schwach belegt, heute": "Weakly evidenced, today",
  "Annahme – beobachten": "Assumption, keep watching",
  Chance: "Opportunity",
  "Stärke halten": "Keep the strength",
  Beobachten: "Watch",
  Nebensache: "Minor",
};

export const OFFER_GAP_EN: Record<string, string> = {
  not_offered: "Gap: not offered",
  optional: "Only optional",
  standard: "Standard feature",
  unknown: "Offer unknown",
};

export const CLASS_EN: Record<string, string> = {
  plattformweit: "Platform-wide",
  modellspezifisch: "Model-specific",
  marktspezifisch: "Market-specific",
  einzeln: "Single scenario",
  gemischt: "Mixed",
  "nicht oben": "Not on top",
};

// Studienvorschläge und Datenlücken kommen ebenfalls deutsch aus core/insights.py.
export const STUDY_EN: Record<string, string> = {
  "Design-Klinik mit Bildvarianten": "Design clinic with image variants",
  "Sitzprobe / Interieur-Klinik": "Seating test / interior clinic",
  "Raum- und Alltags-Test mit Bestandskunden": "Space and everyday-use test with current owners",
  "Bedien-Usability-Test (Blindbedienung, Aufgabenzeit)": "Usability test (eyes-off operation, task time)",
  "Probefahrt-Befragung nach Antriebsart": "Test-drive survey by drivetrain",
  "Lade-Tagebuch-Studie mit BEV-Fahrern": "Charging diary study with EV drivers",
  "Assistenz-Akzeptanz-Befragung": "Driver-assistance acceptance survey",
  "Haptik- und Qualitäts-Klinik": "Haptics and quality clinic",
  "Conjoint-Analyse zu Paketen und Preisen": "Conjoint study on packages and prices",
};

export const GAP_EN: Record<string, string> = {
  "Keine Kundenkommentare für diesen Markt: Befunde stützen sich nur auf Studie, Absatz und Web.": "No customer comments for this market: findings rest on study, sales and web only.",
  "Keine Kundenstudie: Zufriedenheitslücken sind nicht messbar.": "No customer study: satisfaction gaps cannot be measured.",
  "Keine Absatzzahlen: Reichweite ist geschätzt.": "No sales figures: reach is estimated.",
  "Keine Optionsliste: wir wissen nicht, was es heute schon gibt.": "No option list: we do not know what is offered today.",
  "Keine Webbelege: Wettbewerb und Trends fehlen.": "No web evidence: competitors and trends are missing.",
};

export const en = (map: Record<string, string>, key: string) => map[key] ?? key;
