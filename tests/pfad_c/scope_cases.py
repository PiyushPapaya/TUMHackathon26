"""Testmenge für den Scope-Wächter (W-C12): 48 erfundene Befunde, synthetisch, keine BMW-Daten.

Je 9-10 Wünsche, die laut Brief NICHT in unseren Scope gehören (Regulatorik, Engineering-Spezifikation, Preis/
Business-Case), und 20 normale Kundenwünsche als Gegenprobe: Ein Filter, der alles verwirft, wäre wertlos.
Der Wortlaut ist wie echte Befund-Zusammenfassungen gehalten ("Customers ask that ..."), damit die KI urteilen muss
und nicht an Stichwörtern hängt. Die Gegenprobe enthält bewusst Zahlen und Technik-Nähe ("Range: 600 or 700 miles?",
BMW-Folie), die trotzdem Kundenwert sind.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.models import Category, Signal, SignalKind, SourceType

C = Category


@dataclass(frozen=True)
class Case:
    id: str
    label: str  # regulatory | engineering | price | in_scope
    category: Category
    title: str
    summary: str
    kind: SignalKind = SignalKind.UNMET_NEED


CASES: list[Case] = [
    # --- Regulatorik / Zulassung (8) -------------------------------------------------------------------------
    Case("SCOPE-R01", "regulatory", C.DRIVER_ASSISTANCE, "Level 3 homologation",
         "Customers ask that the car gets type approval for Level 3 automated driving in Germany."),
    Case("SCOPE-R02", "regulatory", C.EXTERIOR, "Pedestrian protection rules",
         "Customers ask that the front end meets the new EU pedestrian protection regulation."),
    Case("SCOPE-R03", "regulatory", C.DRIVING_EXPERIENCE, "California emission limits",
         "Customers ask that the powertrain complies with the CARB emission limits in all US states."),
    Case("SCOPE-R04", "regulatory", C.INTERIOR, "Airbag certification",
         "Customers ask that the rear seat airbags obtain FMVSS 208 certification."),
    Case("SCOPE-R05", "regulatory", C.INFOTAINMENT_DIGITAL, "China certification",
         "Customers ask that the infotainment system passes CCC certification for the Chinese market."),
    Case("SCOPE-R06", "regulatory", C.DRIVER_ASSISTANCE, "Cybersecurity approval",
         "Customers ask that the vehicle fulfils UN R155 cybersecurity type approval."),
    Case("SCOPE-R07", "regulatory", C.RANGE_CHARGING, "Battery passport regulation",
         "Customers ask that the battery complies with the EU battery passport regulation."),
    Case("SCOPE-R08", "regulatory", C.INFOTAINMENT_DIGITAL, "GDPR compliance",
         "Customers ask that the driver profile satisfies every GDPR requirement for data storage."),
    Case("SCOPE-R09", "regulatory", C.EXTERIOR, "Headlight beam rules",
         "Customers ask that the headlights follow the ECE R112 beam pattern rules in every market."),
    # --- Engineering-Spezifikation (9) ------------------------------------------------------------------------
    Case("SCOPE-E01", "engineering", C.RANGE_CHARGING, "800 V architecture",
         "Customers ask that the car uses an 800 V electrical architecture."),
    Case("SCOPE-E02", "engineering", C.INTERIOR, "Magnetic encoder part",
         "Customers ask that the volume knob uses a 12-bit magnetic rotary encoder."),
    Case("SCOPE-E03", "engineering", C.RANGE_CHARGING, "22 kW onboard charger",
         "Customers ask that the onboard AC charger is upgraded to 22 kW."),
    Case("SCOPE-E04", "engineering", C.INFOTAINMENT_DIGITAL, "Cockpit chip",
         "Customers ask that the cockpit computer uses the Snapdragon 8295 chip."),
    Case("SCOPE-E05", "engineering", C.COMFORT_SPACE, "Glass thickness",
         "Customers ask that the side windows use 4.5 mm thick laminated glass."),
    Case("SCOPE-E06", "engineering", C.RANGE_CHARGING, "Solid-state cells",
         "Customers ask that the battery uses solid-state cells with 400 Wh/kg."),
    Case("SCOPE-E07", "engineering", C.DRIVING_EXPERIENCE, "Brake disc diameter",
         "Customers ask that the front brake discs have a diameter of 395 mm."),
    Case("SCOPE-E08", "engineering", C.DRIVER_ASSISTANCE, "Lidar supplier",
         "Customers ask that highway assist uses a lidar sensor from a named supplier."),
    Case("SCOPE-E09", "engineering", C.COMFORT_SPACE, "Seat foam density",
         "Customers ask that the seat cushion uses foam with a density of 55 kg per cubic meter."),
    # --- Preis / Business-Case (10) ----------------------------------------------------------------------------
    Case("SCOPE-P01", "price", C.VARIANTS_PACKAGES, "Lower base price",
         "Customers ask that the base price is lowered below 50,000 USD."),
    Case("SCOPE-P02", "price", C.VARIANTS_PACKAGES, "Cheaper lease",
         "Customers ask that the monthly lease rate is cheaper than the Mercedes competitor."),
    Case("SCOPE-P03", "price", C.VARIANTS_PACKAGES, "Free packages",
         "Customers ask that all option packages are included in the base price at no charge."),
    Case("SCOPE-P04", "price", C.VARIANTS_PACKAGES, "Comfort package discount",
         "Customers ask that the Comfort package costs 30 percent less."),
    Case("SCOPE-P05", "price", C.QUALITY_PERCEPTION, "Residual value guarantee",
         "Customers ask that BMW guarantees a residual value of 60 percent after five years."),
    Case("SCOPE-P06", "price", C.VARIANTS_PACKAGES, "Dealer margin",
         "Customers ask that dealers earn a lower margin on optional extras."),
    Case("SCOPE-P07", "price", C.QUALITY_PERCEPTION, "Production cost",
         "Customers ask that BMW cuts the production cost per car by 8 percent."),
    Case("SCOPE-P08", "price", C.INFOTAINMENT_DIGITAL, "Subscription price",
         "Customers ask that heated seats are offered as a subscription at 15 USD per month."),
    Case("SCOPE-P09", "price", C.VARIANTS_PACKAGES, "Option too expensive",
         "Customers complain that the heated steering wheel is too expensive as an option.", SignalKind.COMPLAINT),
    Case("SCOPE-P10", "price", C.VARIANTS_PACKAGES, "Financing offer",
         "Customers ask that BMW offers 0 percent financing on the new model."),
    # --- Gegenprobe: normale Kundenwünsche, dürfen NICHT verworfen werden (16) --------------------------------
    Case("SCOPE-N01", "in_scope", C.INFOTAINMENT_DIGITAL, "Voice control misses commands",
         "Customers complain that voice control often misunderstands simple commands while driving.",
         SignalKind.COMPLAINT),
    Case("SCOPE-N02", "in_scope", C.COMFORT_SPACE, "Seats too short on thigh support",
         "Customers ask for longer thigh support on the front seats for tall drivers."),
    Case("SCOPE-N03", "in_scope", C.INTERIOR, "Cup holders too small",
         "Customers complain that the cup holders are too small for common bottles.", SignalKind.COMPLAINT),
    Case("SCOPE-N04", "in_scope", C.INFOTAINMENT_DIGITAL, "Wireless phone charging unreliable",
         "Customers complain that the wireless charging pad often stops charging the phone.", SignalKind.COMPLAINT),
    Case("SCOPE-N05", "in_scope", C.COMFORT_SPACE, "Hands-free tailgate opens late",
         "Customers complain that the hands-free tailgate needs several attempts to open.", SignalKind.COMPLAINT),
    Case("SCOPE-N06", "in_scope", C.DRIVING_EXPERIENCE, "Ride too harsh on bad roads",
         "Customers complain that the ride feels harsh on broken pavement.", SignalKind.COMPLAINT),
    Case("SCOPE-N07", "in_scope", C.INTERIOR, "Ambient lighting too limited",
         "Customers ask for more colors and brightness settings in the ambient lighting."),
    Case("SCOPE-N08", "in_scope", C.INFOTAINMENT_DIGITAL, "Head-up display hard to read",
         "Customers complain that the head-up display is hard to read in bright sunlight.", SignalKind.COMPLAINT),
    Case("SCOPE-N09", "in_scope", C.RANGE_CHARGING, "Range: 600 or 700 miles?",
         "Customers ask for a real-world range of at least 600 miles on one tank or charge."),
    Case("SCOPE-N10", "in_scope", C.RANGE_CHARGING, "Hard to find compatible chargers",
         "Customers complain that finding a compatible fast charger on trips is slow and confusing.",
         SignalKind.COMPLAINT),
    Case("SCOPE-N11", "in_scope", C.COMFORT_SPACE, "Seat memory forgets positions",
         "Customers complain that the memory seat does not restore their saved position reliably.",
         SignalKind.COMPLAINT),
    Case("SCOPE-N12", "in_scope", C.EXTERIOR, "Door handles freeze in winter",
         "Customers complain that flush door handles do not open in freezing weather.", SignalKind.COMPLAINT),
    Case("SCOPE-N13", "in_scope", C.INFOTAINMENT_DIGITAL, "Climate needs the touchscreen",
         "Customers ask for physical buttons for temperature and fan speed that work without looking.",),
    Case("SCOPE-N14", "in_scope", C.COMFORT_SPACE, "Rear legroom smaller than rivals",
         "Customers ask that rear legroom is at least as good as the main competitors."),
    Case("SCOPE-N15", "in_scope", C.DRIVING_EXPERIENCE, "Wind noise at highway speed",
         "Customers complain that wind noise is distracting above 70 mph.", SignalKind.COMPLAINT),
    Case("SCOPE-N16", "in_scope", C.DRIVER_ASSISTANCE, "Lane keeping too nervous",
         "Customers complain that lane keeping assist steers abruptly in curves.", SignalKind.COMPLAINT),
    # Knifflig: Technik- oder Preisnähe, aber echter Kundenwert (Brief: Varianten und Pakete sind in scope)
    Case("SCOPE-N17", "in_scope", C.RANGE_CHARGING, "Charge state not visible",
         "Customers ask that the charge port light shows the charging state at a glance."),
    Case("SCOPE-N18", "in_scope", C.INTERIOR, "No power outlet in trunk",
         "Customers ask for a 12 V socket in the trunk to run a cooler box."),
    Case("SCOPE-N19", "in_scope", C.INFOTAINMENT_DIGITAL, "Screen glare",
         "Customers complain that the center screen is hard to read because of glare.", SignalKind.COMPLAINT),
    Case("SCOPE-N20", "in_scope", C.VARIANTS_PACKAGES, "Heated wheel not in winter package",
         "Customers ask that the heated steering wheel is part of the cold weather package."),
]


def signals_for_cases() -> list[Signal]:
    """Jeder Fall als Befund (je 20 Nennungen, nur Kundenfeedback), in der Reihenfolge von CASES."""
    return [Signal(id=c.id, kind=c.kind, category=c.category, title=c.title, summary=c.summary,
                   evidence_ids=["EV-SCOPE"], mention_count=20, source_types=[SourceType.FEEDBACK]) for c in CASES]
