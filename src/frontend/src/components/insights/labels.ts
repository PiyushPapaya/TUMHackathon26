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

export const en = (map: Record<string, string>, key: string) => map[key] ?? key;
