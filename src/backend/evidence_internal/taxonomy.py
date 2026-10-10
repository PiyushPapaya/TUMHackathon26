"""Pfad A, A5: BMW-Themen (Vfc level2 Name) -> unsere 9 Kundensicht-Kategorien. Ohne LLM.

Warum von Hand und nicht per LLM: Die Zuordnung ist eine inhaltliche Entscheidung des Teams, sie muss
reproduzierbar und im Pitch erklärbar sein. Gemappt sind die Themen mit >= 20 Nennungen aus allen drei
Feedback-Dateien (112 von 227 Werten, ~90 % der Kommentare mit Thema). Seltene Themen bleiben None und
fallen damit weg; sie würden ohnehin an der Mindestgröße von 5 Nennungen scheitern.

Wer ein Thema umhängt, ändert nur diese Datei. Der Test prüft, dass kein Thema doppelt vorkommt.
"""

from __future__ import annotations

from core.models import Category as C

_BY_CATEGORY: dict[C, tuple[str, ...]] = {
    C.EXTERIOR: (
        "Exterior design", "Exterior", "Wheels / tires", "RSC tire", "Exterior lighting",
        "Exterior rearview mirror", "Panorama glass roof",
    ),
    C.INTERIOR: (
        "Interior design", "Interior", "Ambient light", "Vehicle interior, lighting",
        "Upholstery / interior trim", "Door, finisher panel, front", "Center console, front", "Instrument panel",
    ),
    C.COMFORT_SPACE: (
        "Seats", "Interior comfort", "Space / spatial impression", "Luggage compartment", "Vehicle, climatization",
        "Seating, ventilate / heat", "Seat massage", "Seat memory", "Air conditioning, setting",
        "Air conditioning control panel", "Blower function", "Heated steering wheel", "Sun protection", "Glove box",
        "Cupholder", "Storage compartments", "Seat belts", "Door, open / close", "Door, front", "Automatic doors",
        "Trunk lid, open / close", "Trunk lid", "non-contact trunk lid opening", "Side window, open / close",
        "Vehicle, access and exit", "Resting state after door opening", "Vehicle key", "Vehicle, lock / unlock",
        "Comfort Access", "Interior mirror, garage door opener",
    ),
    C.INFOTAINMENT_DIGITAL: (
        "Touch screen, operation", "ConnectedDrive and Infotainment, overall technology",
        "Operating concept, operating system", "Navigation", "Audio mode, sound", "Apple CarPlay",
        "My BMW App / MINI App", "Head-Up Display", "Instrument cluster", "Intelligent Personal Assistant",
        "Intelligent Personal Assistant, activation word", "Personal eSIM", "Driver profile", "USB port",
        "Rear seat entertainment", "Mobile device, wireless charging", "Remote Software Upgrade/RSU",
        "Radio function", "Manage / pair mobile device (Bluetooth)", "Voice control / speech recognition",
        "WiFi hotspot", "Apps (in-car)", "Gesture control", "Digital Key",
        "Remote Services & Remote Keyless Entry (My BMW App/MINI App)", "Remote Engine Start (My BMW App / MINI App)",
    ),
    C.DRIVING_EXPERIENCE: (
        "Drivetrain", "Drive, driving dynamics and chassis, overall technology", "Handling / Riding",
        "My Modes / driving experience", "Cushioning / damping vehicle", "Braking", "Transmission", "Steering",
        "Steering wheel", "Engine acoustics / engine sound", "Automatic engine start-stop function (MSA)",
        "Operate selector lever", "Automatic-hold", "Brake Energy Regeneration / recuperation",
    ),
    C.RANGE_CHARGING: (
        "Electric Range", "Public charging / external providers", "Charge high-voltage battery",
        "High voltage battery", "Wallbox, charging / home charging", "Opening/closing charging socket cover",
    ),
    C.DRIVER_ASSISTANCE: (
        "Driver assistance, automated driving, overall technology", "Highway assistant", "(Active) cruise control",
        "Parking Assistant", "Rear view camera", "Lane departure warning", "Park Distance Control (PDC)",
        "Steering and lane guide assist", "Surround View", "All-round view", "Speed Limit Assistant",
        "Impression of safety", "Vehicle safety, overall technology",
    ),
    C.QUALITY_PERCEPTION: ("Interior acoustics", "Vehicle battery"),
    C.VARIANTS_PACKAGES: ("Accessories / Parts",),
}  # fmt: skip

VFC2_TO_CATEGORY: dict[str, C] = {name: category for category, names in _BY_CATEGORY.items() for name in names}

# Bewusst nicht gemappt, mit Grund (v1): keine Kundenanforderung oder Thema nicht eindeutig.
IGNORED_VFC2: dict[str, str] = {
    "no_class_found": "BMW hat den Kommentar nicht eingeordnet",
    "Body equipment, overall technology": "Sammelbegriff aus Funktion, Bedienbarkeit und Verarbeitung, nicht eindeutig",
    "Owner's Manual": "Dokumentation, keine Produktanforderung",
    "General enquiry: customer feedback": "allgemeine Anfrage ohne Produktthema",
}

# Quelle D hat kein vfc2, der Bereich steht im festen Satz "... love most about <Bereich> ...".
# Reihenfolge zählt: der erste Treffer gewinnt. Unklare Sätze (z. B. "setting up and starting") bleiben ohne Kategorie.
SURVEY_D_AREAS: tuple[tuple[str, str, C], ...] = (
    ("driving feel", "driving feel", C.DRIVING_EXPERIENCE),
    ("driving comfort", "driving comfort", C.DRIVING_EXPERIENCE),
    ("engine", "engine/motor", C.DRIVING_EXPERIENCE),
    ("getting in", "getting in/out", C.COMFORT_SPACE),
    ("interior", "interior", C.INTERIOR),
    ("infotainment", "infotainment system", C.INFOTAINMENT_DIGITAL),
    ("exterior", "exterior styling", C.EXTERIOR),
    ("feeling of safety", "feeling of safety", C.DRIVER_ASSISTANCE),
)


def category_for_vfc2(name: str) -> C | None:
    return VFC2_TO_CATEGORY.get(name.strip())


def survey_area(text: str) -> tuple[str, C] | None:
    """Bereich aus dem Umfragesatz der Quelle D: ('Survey D, driving feel', Kategorie) oder None."""
    marker = "most about"
    lowered = text.lower()
    if marker not in lowered:
        return None
    phrase = lowered.rsplit(marker, 1)[1]
    for keyword, label, category in SURVEY_D_AREAS:
        if keyword in phrase:
            return f"Survey D, {label}", category
    return None
