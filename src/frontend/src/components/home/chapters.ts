import type { HomeData } from "./useHomeData";

export type Chapter = {
  n: string;
  title: string;
  text: string;
  // Jede Zahl ist ein Zähler, der beim Scrollen hochläuft. value null = Backend nicht erreichbar.
  figures: { label: string; value: number | null }[];
};

// Die vier Kapitel der Scroll-Story entsprechen den vier Schritten des Produkts.
export function buildChapters(d: HomeData): Chapter[] {
  const f = d.funnels[d.mainId];
  const lv = d.levels;
  return [
    { n: "01", title: "Listen.", text: "We read every customer voice: reviews, surveys, forums.", figures: [{ label: "customer voices", value: f?.evidence ?? null }] },
    { n: "02", title: "Find signals.", text: "Repeated complaints and unmet needs become findings, each with its source.", figures: [{ label: "findings", value: f?.signals ?? null }] },
    {
      n: "03",
      title: "Prove it.",
      text: "Every requirement gets a traffic light: green is proven by customers, yellow is weak, red is only an assumption.",
      // Gleiche Ampel wie im Cockpit (badges.tsx): A+B grün, C gelb, D rot.
      figures: [
        { label: "green · proven", value: lv ? lv.A + lv.B : null },
        { label: "yellow · weak", value: lv ? lv.C : null },
        { label: "red · assumption", value: lv ? lv.D : null },
      ],
    },
    { n: "04", title: "Decide.", text: d.topTitle ? `Ranked, explained, auditable. Rank 1: ${d.topTitle}.` : "Ranked, explained, auditable.", figures: [{ label: "requirements", value: f?.requirements ?? null }] },
  ];
}
