"""Pfad A, A5: Studien-Attribute -> Feedback-Thema (vfc2) bzw. Kategorie. Ohne LLM.

Warum: Ein Studienwert ("Navigation system: 16 % unzufrieden") soll am passenden Feedback-Befund
hängen, damit ein Befund zwei Quellenarten hat (-> höhere Evidenzstufe bei Pfad C).

Zwei Ebenen:
1. Direkte Zuordnung Attribut -> vfc2 (US-Studie, genau benannt).
2. Fallback über Stichwörter -> nur Kategorie (CN/EU-Studie hat andere Namen).
Preis, Wert, Marke und Garantie liegen laut Brief nicht im Umfang und werden nie zum Befund.
"""

from __future__ import annotations

from core.models import Category as C
from evidence_internal.taxonomy import category_for_vfc2

OUT_OF_SCOPE_WORDS = (
    "price", "value for money", "resale", "trade-in", "warranty", "afford", "cost of ownership",
    "brand", "reputation", "prestige", "image", "deal offered", "environm",
)  # fmt: skip

STUDY_TO_VFC2: dict[str, str] = {
    "Overall exterior styling": "Exterior design",
    "Appearance of tires/ wheels": "Wheels / tires",
    "Headlight/ taillight design": "Exterior lighting",
    "Overall interior styling/ aesthetics": "Interior design",
    "Interior lighting": "Ambient light",
    "Instrument panel (IP)": "Instrument panel",
    "Cupholders": "Cupholder",
    "Interior storage": "Storage compartments",
    "Overall comfort of the seats": "Seats",
    "Comfort of front seat": "Seats",
    "Comfort of 2nd row seat": "Seats",
    "Interior roominess": "Space / spatial impression",
    "Front seat roominess": "Space / spatial impression",
    "2nd row seat roominess": "Space / spatial impression",
    "Cargo capacity/usefulness": "Luggage compartment",
    "Trunk lid/ tailgate and liftgate operations": "Trunk lid, open / close",
    "Overall performance of climate control system": "Vehicle, climatization",
    "Heater performance": "Vehicle, climatization",
    "Air conditioner performance": "Vehicle, climatization",
    "Operation of heater/ AC controls": "Air conditioning control panel",
    "Handling/Maneuverability": "Handling / Riding",
    "Riding comfort": "Cushioning / damping vehicle",
    "Overall power and pickup": "Drivetrain",
    "Smoothness of transmission": "Transmission",
    "Braking": "Braking",
    "Sound of engine": "Engine acoustics / engine sound",
    "Overall performance of sound system": "Audio mode, sound",
    "Gas or electric mileage (fuel economy)": "Electric Range",
    "Overall safety of the vehicle": "Impression of safety",
    "Overall driver assist features": "Driver assistance, automated driving, overall technology",
    "If applicable: Backup system (camera, sensors, etc.)": "Rear view camera",
    "Adaptive driving assists (lane keeping, cruise, braking)": "(Active) cruise control",
    "Overall driver-vehicle interaction (HMI)": "Operating concept, operating system",
    "Menu structure of infotainment system": "Operating concept, operating system",
    "If applicable: Navigation system": "Navigation",
    "Navigation system": "Navigation",
    "Integrated navigation system": "Navigation",
    "Bluetooth/ smartphone pairing": "Manage / pair mobile device (Bluetooth)",
    "WiFi hotspot in vehicle": "WiFi hotspot",
    "Mirroring of smartphone content on vehicle display": "Apple CarPlay",
    "Phone charging": "Mobile device, wireless charging",
    "Head-up Display": "Head-Up Display",
    "Performance of voice recognition": "Voice control / speech recognition",
    "Vehicle's Mobile App": "My BMW App / MINI App",
    "If applicable: Sunroof/ moonroof": "Panorama glass roof",
    # CN/EU-Studie (andere Namen als die US-Studie)
    "Exterior styling": "Exterior design",
    "Interior styling": "Interior design",
    "Safety": "Impression of safety",
    "All round visibility": "All-round view",
    "Smartphone integration/ connectivity": "Apple CarPlay",
    "Features of information and entertainment system including in-car apps":
        "ConnectedDrive and Infotainment, overall technology",
    "Easy to use information and entertainment system including in-car apps":
        "Operating concept, operating system",
    "Connected services": "My BMW App / MINI App",
    "Overall seating comfort": "Seats",
    "Interior storage for small items": "Storage compartments",
    "Acceleration": "Drivetrain",
    "Roadholding": "Handling / Riding",
    "Manoeuvrability": "Handling / Riding",
    "Quality of ride": "Cushioning / damping vehicle",
    "Fuel economy/ energy efficiency": "Electric Range",
    "Front interior roominess": "Space / spatial impression",
    "Rear interior roominess": "Space / spatial impression",
    "Ease of loading/ unloading luggage": "Luggage compartment",
    "Luggage capacity": "Luggage compartment",
    "Ease of entry into and out of car": "Vehicle, access and exit",
    "Heating/ ventilation/ air conditioning": "Vehicle, climatization",
    "Quietness when driving": "Interior acoustics",
}  # fmt: skip

# Fallback (erster Treffer gewinnt, Kleinbuchstaben). Nur für Attribute ohne direkte Zuordnung.
KEYWORD_CATEGORY: tuple[tuple[tuple[str, ...], C], ...] = (
    (("exterior", "headlight", "tire", "wheel", "door handle"), C.EXTERIOR),
    (("seat", "room", "cargo", "luggage", "storage", "heating", "climate", "entry", "versatil"), C.COMFORT_SPACE),
    (("interior",), C.INTERIOR),
    (("navigation", "smartphone", "connect", "entertainment", "display", "screen", "voice", "apps", "wifi"),
     C.INFOTAINMENT_DIGITAL),
    (("assist", "camera", "visibility", "safety", "monitoring"), C.DRIVER_ASSISTANCE),
    (("range", "charging", "electric", "fuel economy", "energy"), C.RANGE_CHARGING),
    (("squeak", "rattle", "quiet", "noise", "durab", "reliab", "build quality", "faults", "electrical", "solid"),
     C.QUALITY_PERCEPTION),
    (("driv", "handling", "acceler", "roadholding", "braking", "sporti", "ride", "power", "passing", "steer",
      "manoeuv", "turning", "transmission", "off-road"), C.DRIVING_EXPERIENCE),
)  # fmt: skip


def study_vfc2(attribute: str) -> str | None:
    return STUDY_TO_VFC2.get(attribute.strip())


def study_category(attribute: str) -> C | None:
    """Kategorie eines Studienattributs, None wenn außerhalb des Umfangs oder nicht zuordenbar."""
    name = attribute.strip()
    if any(word in name.lower() for word in OUT_OF_SCOPE_WORDS):
        return None
    vfc2 = STUDY_TO_VFC2.get(name)
    if vfc2 and (category := category_for_vfc2(vfc2)):
        return category
    lowered = name.lower()
    for words, category in KEYWORD_CATEGORY:
        if any(word in lowered for word in words):
            return category
    return None
