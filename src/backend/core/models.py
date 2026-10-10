"""Gemeinsames Datenmodell (der Vertrag zwischen allen Pfaden).

Warum Pydantic: Jede Stufe der Pipeline (Beleg -> Befund -> Anforderung -> Entscheidung)
gibt genau diese Objekte weiter. Pydantic prüft die Felder beim Erzeugen, damit ein
Fehler in Pfad A nicht erst im Frontend von Pfad D auffällt. FastAPI erzeugt daraus
automatisch die Doku unter /docs.

Änderungen hier NUR per PR von Piyush (Lead), weil alle Pfade davon abhängen.
Spiegelbild für Menschen: src/shared/API.md und src/shared/beispiele/*.json.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from core.model_parts import (
    BusinessContext,
    DataCoverage,
    Horizon,
    Robustness,
    SegmentConflict,
    StudyLink,
)


class SourceType(StrEnum):
    """Woher ein Beleg stammt. Bestimmt, wie stark er für die Evidenzstufe zählt."""

    FEEDBACK = "feedback"          # Kundenfeedback (Excel, Quellen A-D)
    STUDY = "study"                # Kundenstudie (Zufriedenheitswerte)
    SALES = "sales"                # Absatzvolumen pro Markt
    OPTION_LIST = "option_list"    # Preisliste/Ausstattung (heutiges Angebot)
    WEB = "web"                    # externe Webquelle (Wettbewerb, Trends, Tests)
    EXTERNAL_STAT = "external_stat"            # öffentliche Statistik (z. B. Ladesäulen, EPA-Reichweite)
    FEEDBACK_EXTERNAL = "feedback_external"    # externe Kundenstimme (z. B. NHTSA-Beschwerden)


class Category(StrEnum):
    """Kundensicht-Kategorien aus dem Brief ("In scope")."""

    EXTERIOR = "exterior"
    INTERIOR = "interior"
    COMFORT_SPACE = "comfort_space"
    INFOTAINMENT_DIGITAL = "infotainment_digital"
    DRIVING_EXPERIENCE = "driving_experience"
    RANGE_CHARGING = "range_charging"
    DRIVER_ASSISTANCE = "driver_assistance"
    QUALITY_PERCEPTION = "quality_perception"
    VARIANTS_PACKAGES = "variants_packages"


class SignalKind(StrEnum):
    """Arten von Befunden, wie im Brief genannt."""

    COMPLAINT = "complaint"                        # wiederkehrende Beschwerde
    UNMET_NEED = "unmet_need"                      # unerfüllter Wunsch
    DELIGHT = "delight"                            # Stärke, die erhalten bleiben muss
    COMPETITOR_ADVANTAGE = "competitor_advantage"  # Wettbewerber ist besser
    TREND = "trend"                                # Markt-/Technologietrend (3-5 Jahre)


class EvidenceLevel(StrEnum):
    """Wie belastbar ist eine Anforderung? Regeln: requirements_engine/evidence_level.py."""

    A = "A"  # stark: mehrere unabhängige Quellenarten, viele Nennungen
    B = "B"  # mittel: eine Quellenart mit vielen Nennungen
    C = "C"  # schwach: wenige Nennungen oder nur Web
    D = "D"  # Annahme: zukunftsgerichtet, kaum direkte Belege


class Status(StrEnum):
    PROPOSED = "proposed"      # von der KI vorgeschlagen, wartet auf PM
    CHALLENGED = "challenged"  # PM hat nachgefragt, KI hat geantwortet
    APPROVED = "approved"
    REJECTED = "rejected"


class ActorType(StrEnum):
    AI = "ai"
    HUMAN = "human"
    SYSTEM = "system"


class Actor(BaseModel):
    type: ActorType
    name: str = Field(examples=["pm.mueller", "gpt-5-mini", "pipeline"])


class Evidence(BaseModel):
    """Ein einzelner Beleg: ein Kundenkommentar, ein Studienwert, eine Webquelle."""

    id: str = Field(examples=["EV-G60-0042"])
    source_type: SourceType
    source_name: str = Field(examples=["Feedback Quelle B", "US-Studie 2025", "caranddriver.com"])
    derivative: str = Field(examples=["G60"])
    market: str = Field(examples=["US"])
    text: str                     # Originalzitat oder Kennzahl als Satz
    url: str | None = None        # nur bei Webquellen
    retrieved_at: datetime | None = None
    polarity: int = Field(0, ge=-1, le=1)  # -1 negativ, 0 neutral, +1 positiv
    meta: dict[str, str] = {}     # Schlüssel u. a.: engine, country, source_letter, feedback_type, vfc2


class Signal(BaseModel):
    """Ein Befund: verdichtete, wiederkehrende Aussage mit Belegen."""

    id: str = Field(examples=["SIG-G60-US-007"])
    kind: SignalKind
    category: Category
    title: str
    summary: str
    evidence_ids: list[str]
    mention_count: int
    source_types: list[SourceType]
    conflicts_with: list[str] = []  # IDs widersprechender Befunde
    # Zählung je Segment, z. B. {"engine": {"BEV": 42, "ICE": 18}, "country": {...}, "source": {...}}
    segments: dict[str, dict[str, int]] = {}
    study_link: StudyLink | None = None


class ScoreFactor(BaseModel):
    """Ein Faktor der Priorisierung. Summe aller contribution = Rohscore."""

    value: float = Field(ge=0, le=1)  # normierter Faktorwert
    weight: float = Field(ge=0, le=1)
    contribution: float               # value * weight * 100
    explanation: str                  # Satz für den PM, z. B. "38 von 3.610 Kommentaren"


class OfferCheck(BaseModel):
    """Gibt es das heute schon im Angebot (Optionsliste)?"""

    status: str = Field(examples=["not_offered", "optional", "standard", "unknown"])
    note: str = ""
    option_code: str | None = None


class Requirement(BaseModel):
    id: str = Field(examples=["REQ-G60-US-003"])
    title: str
    description: str               # kundenorientiert, umsetzbar
    acceptance_criterion: str      # messbares Ziel, z. B. "Lautstärke ohne Blick in 1 Handgriff"
    category: Category
    signal_ids: list[str]
    score: float = Field(ge=0, le=100)
    rank: int
    score_breakdown: dict[str, ScoreFactor]
    rationale: str                 # Begründung der Priorität in 1-2 Sätzen
    evidence_level: EvidenceLevel
    assumptions: list[str]         # zukunftsgerichtete Annahmen
    uncertainties: list[str]
    offer_check: OfferCheck
    effort: str = Field("M", pattern="^(S|M|L)$")  # grober Aufwand, PM kann ändern
    status: Status = Status.PROPOSED
    version: int = 1
    # Welle 2 (alle mit Default, damit alte Bundles gültig bleiben)
    horizon: Horizon = "today"
    robustness: Robustness | None = None
    segment_conflicts: list[SegmentConflict] = []
    business: BusinessContext | None = None
    stable_key: str = ""           # Hash der sortierten signal_ids: gleiche Befunde -> gleiche ID
    badges: list[str] = []         # fertige Kurzlabels fürs Frontend, z. B. "robust", "Zukunftswette"


class AuditEvent(BaseModel):
    """Ein unveränderlicher Eintrag im Prüfpfad (append-only, Hash-Kette)."""

    seq: int
    ts: datetime
    event_type: str = Field(examples=["REQUIREMENT_PROPOSED", "PM_APPROVED", "WEIGHTS_CHANGED"])
    scenario_id: str
    requirement_id: str | None = None
    actor: Actor
    rationale: str
    payload: dict = {}             # z. B. {"before": {...}, "after": {...}}
    prev_hash: str
    hash: str


class Scenario(BaseModel):
    """Ein Fahrzeug in einem Markt. Neues Fahrzeug = neue JSON-Datei in config/scenarios/."""

    id: str = Field(examples=["G60-US"])
    derivative: str
    model_name: str
    market: str
    countries: list[str]
    competitors: list[str]
    successor_horizon: str = "2030"
    data_coverage: DataCoverage = Field(default_factory=DataCoverage)
    warnings: list[str] = []       # z. B. "Nur 19 Kommentare", "3 unbekannte Themen"
