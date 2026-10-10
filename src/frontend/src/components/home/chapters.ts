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
      text: "Every requirement gets an evidence level from A (strong) to D (assumption).",
      figures: (["A", "B", "C", "D"] as const).map((k) => ({ label: `level ${k}`, value: lv ? lv[k] : null })),
    },
    { n: "04", title: "Decide.", text: d.topTitle ? `Ranked, explained, auditable. Rank 1: ${d.topTitle}.` : "Ranked, explained, auditable.", figures: [{ label: "requirements", value: f?.requirements ?? null }] },
  ];
}
