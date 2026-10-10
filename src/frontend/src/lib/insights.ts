// API-Aufrufe für die Ansichten, die api.ts (Vertrag des Leads) noch nicht kennt.
// Warum eine eigene Datei: api.ts bleibt unverändert, neue Endpunkte aus src/shared/API.md kommen hierher.
import type { Evidence, EvidenceLevel, Weights, WeightKey } from "@/src/lib/api";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function get<T>(path: string): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`);
  } catch {
    throw new Error("Backend not reachable – start uvicorn");
  }
  if (!res.ok) throw new Error(`Request failed: ${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

const enc = encodeURIComponent;

export interface MatrixItem {
  horizon: string;
  evidence_level: EvidenceLevel;
  quadrant: string;
  offer_gap: string;
  offer_gap_label: string;
}
export interface MatrixView {
  scenario_id: string;
  successor_horizon: string;
  quadrants: string[];
  items: Record<string, MatrixItem>;
}

export interface OpportunityPoint {
  attribute: string;
  category: string;
  importance: number;
  dissatisfaction: number;
  quadrant: string;
  evidence_id: string | null;
}
export interface OpportunitiesView {
  scenario_id: string;
  points: OpportunityPoint[];
  quadrants: string[];
}

export interface TrendItem {
  topic: string;
  category: string;
  horizon: string;
  kind: "trend" | "bet";
  strength: number;
  sources: string[];
  requirement_id: string | null;
  evidence_level: EvidenceLevel;
  assumptions: string[];
}
export interface TrendsView {
  scenario_id: string;
  successor_horizon: string;
  rings: string[];
  items: TrendItem[];
}

export interface WeakRequirement {
  id: string;
  title: string;
  rank: number;
  evidence_level: EvidenceLevel;
  level_label: string;
  assumptions: string[];
  why: string;
  next_study: string;
}
export interface GapsView {
  scenario_id: string;
  weak_requirements: WeakRequirement[];
  missing_sources: string[];
  share_weak: number;
}

export interface PortfolioCell {
  requirement_id: string;
  title: string;
  rank: number;
  score: number;
  evidence_level: EvidenceLevel;
  level_label: string;
}
export interface PortfolioView {
  scenarios: { id: string; model_name: string; market: string }[];
  rows: { category: string; cells: Record<string, PortfolioCell | null>; class: string; top_in: string[] }[];
  rule?: string;
}

export interface CompareRow {
  category: string;
  a: PortfolioCell | null;
  b: PortfolioCell | null;
  rank_diff: number | null;
  sentence: string;
}
export interface CompareView {
  a: string;
  b: string;
  rows: CompareRow[];
}

export interface EvidencePage {
  total: number;
  page: number;
  size: number;
  items: Evidence[];
}

export interface LensReason {
  factor: string;
  contribution: number;
  sentence: string;
}
export interface LensResult {
  question: string;
  interpretation: string;
  source: "ai" | "rules";
  weights: Weights;
  note?: string;
  top: {
    requirement: { id: string; title: string; rank: number; evidence_level: EvidenceLevel };
    lens_score: number;
    lens_rank: number;
    reasons: LensReason[];
  }[];
}

export const getMatrix = (id: string) => get<MatrixView>(`/api/scenarios/${enc(id)}/matrix`);
export const getOpportunities = (id: string) => get<OpportunitiesView>(`/api/scenarios/${enc(id)}/opportunities`);
export const getTrends = (id: string) => get<TrendsView>(`/api/scenarios/${enc(id)}/trends`);
export const getGaps = (id: string) => get<GapsView>(`/api/scenarios/${enc(id)}/gaps`);
export const getPortfolio = () => get<PortfolioView>("/api/portfolio");
export const getCompare = (a: string, b: string) => get<CompareView>(`/api/compare?a=${enc(a)}&b=${enc(b)}`);

export function getEvidencePage(id: string, f: { q?: string; segment?: string; page?: number; size?: number }) {
  const qs = new URLSearchParams();
  if (f.q) qs.set("q", f.q);
  if (f.segment) qs.set("segment", f.segment);
  qs.set("page", String(f.page ?? 1));
  qs.set("size", String(f.size ?? 20));
  return get<EvidencePage>(`/api/scenarios/${enc(id)}/evidence?${qs}`);
}

export function postLens(id: string, question: string, actor: string): Promise<LensResult> {
  return fetch(`${BASE_URL}/api/scenarios/${enc(id)}/lens`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, actor }),
  }).then(async (res) => {
    if (!res.ok) throw new Error(res.status === 422 ? "Please type a question." : `Request failed: ${res.status}`);
    return res.json() as Promise<LensResult>;
  });
}

export const getMemoUrl = (id: string) => `${BASE_URL}/api/scenarios/${enc(id)}/memo`;

export type { WeightKey };
