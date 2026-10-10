/**
 * Eine Datei für alle API-Typen und -Aufrufe, weil jede Seite dieselben Typen braucht
 * und sich bei Vertragsänderungen (src/shared/API.md) nur diese Datei ändern soll.
 * Quelle der Wahrheit: src/backend/core/models.py + src/backend/api/routes.py.
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ---------------------------------------------------------------------------
// Typen (gespiegelt aus core/models.py)
// ---------------------------------------------------------------------------

export type SourceType = "feedback" | "study" | "sales" | "option_list" | "web";

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
  derivative: string;
  market: string;
  text: string;
  url: string | null;
  retrieved_at: string | null;
  polarity: -1 | 0 | 1;
  meta: Record<string, string>;
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
}

export interface ScoreFactor {
  value: number;
  weight: number;
  contribution: number;
  explanation: string;
}

export type OfferCheckStatus = "not_offered" | "optional" | "standard" | "unknown";

export interface OfferCheck {
  status: OfferCheckStatus;
  note: string;
  option_code: string | null;
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

export interface Scenario {
  id: string;
  derivative: string;
  model_name: string;
  market: string;
  countries: string[];
  competitors: string[];
  successor_horizon: string;
}

export interface Funnel {
  evidence: number;
  signals: number;
  requirements: number;
  approved: number;
  /** Nur vorhanden, wenn das Beispiel-Bundle geladen wurde (statt echter Pipeline-Daten). */
  note?: string;
}

export interface RequirementDetail {
  requirement: Requirement;
  signals: Signal[];
  evidence: Evidence[];
  history: AuditEvent[];
}

export type DecisionAction = "approve" | "reject" | "edit" | "challenge";

/** Nur diese Felder darf "edit" ändern (siehe API.md). */
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

export interface WeightsInput {
  weights: Partial<
    Record<
      | "customer_pain"
      | "reach"
      | "satisfaction_gap"
      | "competitive_pressure"
      | "future_relevance"
      | "effort_inverse",
      number
    >
  >;
  actor: string;
  rationale: string;
}

export interface AuditVerifyResult {
  valid: boolean;
  broken_at_seq: number | null;
  checked: number;
}

// ---------------------------------------------------------------------------
// Hilfsfunktion: fetch mit lesbarer Fehlermeldung
// ---------------------------------------------------------------------------

/**
 * Wirft eine lesbare Meldung statt eines rohen Response-Objekts, damit die UI
 * direkt `error.message` anzeigen kann ("Backend not reachable – start uvicorn").
 */
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
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

// ---------------------------------------------------------------------------
// Eine fetch-Funktion pro Endpunkt (src/shared/API.md)
// ---------------------------------------------------------------------------

export function getScenarios(): Promise<Scenario[]> {
  return request<Scenario[]>("/api/scenarios");
}

export function getFunnel(scenarioId: string): Promise<Funnel> {
  return request<Funnel>(`/api/scenarios/${encodeURIComponent(scenarioId)}/funnel`);
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

export function getAuditVerify(): Promise<AuditVerifyResult> {
  return request<AuditVerifyResult>("/api/audit/verify");
}

/** Kein fetch, da der Browser den CSV-Download selbst über den Link auslöst. */
export function getExportUrl(scenarioId: string): string {
  return `${BASE_URL}/api/scenarios/${encodeURIComponent(scenarioId)}/export`;
}
