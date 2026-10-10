const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type SourceType =
  | "feedback"
  | "study"
  | "sales"
  | "option_list"
  | "web"
  | "external_stat"
  | "feedback_external";

export type Category =
  | "exterior"
  | "interior"
  | "comfort_space"
  | "infotainment_digital"
  | "driving_experience"
  | "range_charging"
  | "driver_assistance"
  | "quality_perception"
  | "variants_packages";

export type SignalKind =
  | "complaint"
  | "unmet_need"
  | "delight"
  | "competitor_advantage"
  | "trend";

export type EvidenceLevel = "A" | "B" | "C" | "D";
export type RequirementStatus = "proposed" | "challenged" | "approved" | "rejected";
export type Effort = "S" | "M" | "L";
export type ActorType = "ai" | "human" | "system";

export interface Actor {
  type: ActorType;
  name: string;
}

export interface Evidence {
  id: string;
  source_type: SourceType;
  source_name: string;
  derivative?: string;
  market?: string;
  text: string;
  url: string | null;
  retrieved_at: string | null;
  polarity: -1 | 0 | 1;
  meta: Record<string, string | number | boolean | null | undefined>;
}

export interface StudyLink {
  attribute: string;
  importance: number;
  dissatisfaction: number;
}

export interface Signal {
  id: string;
  kind: SignalKind;
  category: Category;
  title: string;
  summary: string;
  evidence_ids: string[];
  mention_count: number;
  source_types: SourceType[];
  conflicts_with: string[];
  segments?: Record<string, Record<string, number>>;
  study_link?: StudyLink | null;
}

export interface ScoreFactor {
  value: number;
  weight: number;
  contribution: number;
  explanation: string;
}

export type OfferCheckStatus = "not_offered" | "optional" | "standard" | "unknown";

export interface OfferCheck {
  status: OfferCheckStatus | string;
  note: string;
  option_code: string | null;
}

export interface Robustness {
  rank_min: number;
  rank_max: number;
  top3_share: number;
  runs: number;
}

export interface SegmentConflict {
  dimension: string;
  segment_a?: string;
  segment_b?: string;
  statement: string;
  a_count?: number;
  b_count?: number;
  evidence_ids?: string[];
  signal_ids?: string[];
}

export interface BusinessContext {
  volume_2025: number | null;
  volume_2030: number | null;
  growth_pct: number | null;
  market_share: number | null;
  note: string;
}

export interface Requirement {
  id: string;
  title: string;
  description: string;
  acceptance_criterion: string;
  category: Category;
  signal_ids: string[];
  score: number;
  rank: number;
  score_breakdown: Record<string, ScoreFactor>;
  rationale: string;
  evidence_level: EvidenceLevel;
  assumptions: string[];
  uncertainties: string[];
  offer_check: OfferCheck;
  effort: Effort;
  status: RequirementStatus;
  version: number;
  horizon?: "today" | "next_gen";
  robustness?: Robustness | null;
  segment_conflicts?: SegmentConflict[];
  business?: BusinessContext | null;
  stable_key?: string;
  badges?: string[];
}

export interface AuditEvent {
  seq: number;
  ts: string;
  event_type: string;
  scenario_id: string;
  requirement_id: string | null;
  actor: Actor;
  rationale: string;
  payload: Record<string, unknown>;
  prev_hash: string;
  hash: string;
}

export interface AuditTimelineEvent {
  seq: number;
  ts: string;
  actor: Actor;
  requirement_id: string | null;
  event_type: string;
  sentence: string;
  rationale: string;
}

export interface DataCoverage {
  feedback: number;
  study: number;
  sales: number;
  options: number;
  web: number;
  external: number;
  badge: string;
}

export interface Scenario {
  id: string;
  derivative: string;
  model_name: string;
  market: string;
  countries: string[];
  competitors: string[];
  successor_horizon: string;
  data_coverage?: DataCoverage;
  badge?: string;
  warnings?: string[];
  headline_numbers?: {
    evidence: number;
    signals: number;
    requirements: number;
    top_title: string | null;
  };
}

export interface Funnel {
  evidence: number;
  signals: number;
  requirements: number;
  approved: number;
  note?: string;
  generated_at?: string | null;
}

export interface OverviewView {
  scenario_id: string;
  funnel: Funnel;
  top3: Array<{
    id: string;
    title: string;
    score: number;
    rank: number;
    evidence_level: EvidenceLevel;
    level_label?: string;
    badges?: string[];
  }>;
  level_distribution: Record<EvidenceLevel, number>;
  warnings: string[];
  source_mix: DataCoverage;
  generated_at: string | null;
}

export interface RequirementDetail {
  requirement: Requirement;
  signals: Signal[];
  evidence: Evidence[];
  history: AuditEvent[];
}

export interface WaterfallStep {
  factor: string;
  label: string;
  value: number;
  weight: number | null;
  contribution: number;
  sentence: string;
}

export interface ExplainView extends RequirementDetail {
  level_label?: string;
  waterfall?: WaterfallStep[];
  quotes?: Array<Record<string, unknown>>;
  segments?: Record<string, Record<string, number>>;
  conflicts?: SegmentConflict[];
  web_sources?: Array<{
    id: string;
    publisher: string;
    url: string | null;
    text: string;
    trust: string;
  }>;
  study?: StudyLink[];
  robustness_sentence?: string | null;
  business?: BusinessContext | null;
}

export type DecisionAction = "approve" | "reject" | "edit" | "challenge";

export interface RequirementEditableChanges {
  title?: string;
  description?: string;
  acceptance_criterion?: string;
  effort?: Effort;
  assumptions?: string[];
  uncertainties?: string[];
}

export interface DecisionInput {
  action: DecisionAction;
  actor: string;
  rationale: string;
  changes?: RequirementEditableChanges;
  question?: string;
}

export interface AiAnswer {
  answer: string;
  supporting_evidence_ids: string[];
  counter_evidence_ids: string[];
  suggested_change: unknown | null;
}

export interface DecisionResult {
  requirement: Requirement;
  ai_answer: AiAnswer | null;
}

export type WeightKey =
  | "customer_pain"
  | "reach"
  | "satisfaction_gap"
  | "competitive_pressure"
  | "future_relevance"
  | "effort_inverse";

export type Weights = Partial<Record<WeightKey, number>>;

export interface WeightsInput {
  weights: Weights;
  actor: string;
  rationale: string;
}

export interface WhatIfRank {
  id: string;
  title: string;
  evidence_level: EvidenceLevel;
  old_rank: number;
  new_rank: number;
  rank_change: number;
  old_score: number;
  new_score: number;
}

export interface AuditVerifyResult {
  valid: boolean;
  broken_at_seq: number | null;
  checked: number;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
      ...init,
    });
  } catch {
    throw new Error("Backend not reachable – start uvicorn");
  }

  if (!response.ok) {
    const detail = await response
      .json()
      .then((body: { detail?: string }) => body.detail)
      .catch(() => undefined);
    throw new Error(detail ?? `Request failed: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

export function getScenarios(): Promise<Scenario[]> {
  return request<Scenario[]>("/api/scenarios");
}

export function getFunnel(scenarioId: string): Promise<Funnel> {
  return request<Funnel>(`/api/scenarios/${encodeURIComponent(scenarioId)}/funnel`);
}

export function getOverview(scenarioId: string): Promise<OverviewView> {
  return request<OverviewView>(`/api/scenarios/${encodeURIComponent(scenarioId)}/overview`);
}

export function getSignals(scenarioId: string): Promise<Signal[]> {
  return request<Signal[]>(`/api/scenarios/${encodeURIComponent(scenarioId)}/signals`);
}

export function getRequirements(scenarioId: string): Promise<Requirement[]> {
  return request<Requirement[]>(`/api/scenarios/${encodeURIComponent(scenarioId)}/requirements`);
}

export function getRequirementDetail(reqId: string): Promise<RequirementDetail> {
  return request<RequirementDetail>(`/api/requirements/${encodeURIComponent(reqId)}`);
}

export function getRequirementExplain(reqId: string): Promise<ExplainView> {
  return request<ExplainView>(`/api/requirements/${encodeURIComponent(reqId)}/explain`);
}

export function postDecision(reqId: string, input: DecisionInput): Promise<DecisionResult> {
  return request<DecisionResult>(`/api/requirements/${encodeURIComponent(reqId)}/decision`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function putWeights(scenarioId: string, input: WeightsInput): Promise<Requirement[]> {
  return request<Requirement[]>(`/api/scenarios/${encodeURIComponent(scenarioId)}/weights`, {
    method: "PUT",
    body: JSON.stringify(input),
  });
}

export function postWhatIf(scenarioId: string, weights: Weights): Promise<WhatIfRank[]> {
  return request<WhatIfRank[]>(`/api/scenarios/${encodeURIComponent(scenarioId)}/whatif`, {
    method: "POST",
    body: JSON.stringify({ weights }),
  });
}

export function getAudit(filter?: {
  scenarioId?: string;
  requirementId?: string;
}): Promise<AuditEvent[]> {
  const params = new URLSearchParams();
  if (filter?.scenarioId) params.set("scenario_id", filter.scenarioId);
  if (filter?.requirementId) params.set("requirement_id", filter.requirementId);
  const query = params.toString();
  return request<AuditEvent[]>(`/api/audit${query ? `?${query}` : ""}`);
}

export function getAuditTimeline(filter?: {
  scenarioId?: string;
  requirementId?: string;
}): Promise<AuditTimelineEvent[]> {
  const params = new URLSearchParams();
  if (filter?.scenarioId) params.set("scenario_id", filter.scenarioId);
  if (filter?.requirementId) params.set("requirement_id", filter.requirementId);
  const query = params.toString();
  return request<AuditTimelineEvent[]>(`/api/audit/timeline${query ? `?${query}` : ""}`);
}

export function getAuditVerify(): Promise<AuditVerifyResult> {
  return request<AuditVerifyResult>("/api/audit/verify");
}

export function getExportUrl(scenarioId: string, format: "csv" | "json" | "md" = "csv"): string {
  return `${BASE_URL}/api/scenarios/${encodeURIComponent(scenarioId)}/export?format=${format}`;
}
