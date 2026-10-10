"""Zeichnet Techflow, Mockups und das Bild "vom Kundenzitat zum Requirement" nach visuals/.

Aufruf aus dem Repo-Root:  python scripts/make_diagrams.py
Warum ein Skript: PNG (für Folien) und SVG (verlustfrei) entstehen aus derselben Quelle,
und jede Person kann Text und Farben ändern, ohne ein Grafikprogramm.
Alle Zahlen in den Mockups sind Beispielwerte. Nur das Zitat G60-0019 stammt aus den echten Daten.
"""

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent.parent / "visuals"
BLAU, BLAU_HELL, ORANGE, ORANGE_HELL = "#1C69D4", "#DBE8FB", "#D9822B", "#FFE7C7"
GRAU, GRAU_HELL, TEXT, GRUEN, GELB, ROT = "#7B8594", "#E8EBF0", "#1B2330", "#2E9E6B", "#E0A030", "#D64545"


def neue_flaeche(breite: float, hoehe: float):
    fig, ax = plt.subplots(figsize=(breite / 100, hoehe / 100))
    ax.set_xlim(0, breite)
    ax.set_ylim(hoehe, 0)  # y läuft nach unten, wie bei Webseiten
    ax.axis("off")
    return fig, ax


def box(ax, x, y, b, h, text="", fuell="white", rand=GRAU, size=10, fett=False, farbe=TEXT, umbruch=None, ha="center"):
    ax.add_patch(FancyBboxPatch((x, y), b, h, boxstyle="round,pad=0,rounding_size=8", fc=fuell, ec=rand, lw=1.4))
    if text:
        if umbruch:
            text = "\n".join(textwrap.fill(z, umbruch) for z in text.split("\n"))
        tx = x + b / 2 if ha == "center" else x + 10
        ax.text(tx, y + h / 2, text, ha=ha, va="center", fontsize=size, color=farbe, weight="bold" if fett else "normal")


def pfeil(ax, x1, y1, x2, y2, farbe=GRAU):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=farbe, lw=1.6))


def speichern(fig, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for endung in ("png", "svg"):
        fig.savefig(OUT / f"{name}.{endung}", dpi=150, bbox_inches="tight", facecolor="white")
        print("geschrieben:", OUT / f"{name}.{endung}")
    plt.close(fig)


def techflow() -> None:
    fig, ax = neue_flaeche(1600, 520)
    ax.text(10, 28, "Signal2Spec: der Weg der Daten", fontsize=16, weight="bold", color=TEXT)
    schritte = [
        ("1 Einlesen", "Excel → Belege\nmit fester ID", GRAU_HELL, GRAU),
        ("2 Befunde", "Themen bilden,\nKI fasst zusammen", BLAU_HELL, BLAU),
        ("3 Web", "Wettbewerb, Trends\nmit URL", BLAU_HELL, BLAU),
        ("4 Anforderung", "KI entwirft,\nCode prüft Scope", BLAU_HELL, BLAU),
        ("5 Priorität", "Formel + Evidenz-\nstufe A-D", GRAU_HELL, GRAU),
        ("6 PM-Entscheid", "approve · reject\nedit · challenge", ORANGE_HELL, ORANGE),
        ("7 Audit Trail", "jede Änderung,\nHash-Kette", GRAU_HELL, GRAU),
    ]
    b, h, luecke, y = 190, 150, 40, 130
    for i, (titel, sub, fuell, rand) in enumerate(schritte):
        x = 10 + i * (b + luecke)
        box(ax, x, y, b, h, "", fuell, rand)
        ax.text(x + b / 2, y + 40, titel, ha="center", va="center", fontsize=11, weight="bold", color=TEXT)
        ax.text(x + b / 2, y + 95, sub, ha="center", va="center", fontsize=9, color=TEXT)
        if i < len(schritte) - 1:
            pfeil(ax, x + b + 4, y + h / 2, x + b + luecke - 4, y + h / 2)
    # Challenge-Schleife: von 6 zurück zu 4
    x4, x6 = 10 + 3 * (b + luecke) + b / 2, 10 + 5 * (b + luecke) + b / 2
    ax.plot([x6, x6, x4, x4], [y + h, y + h + 55, y + h + 55, y + h + 4], color=ORANGE, lw=1.6, ls="--")
    ax.text((x4 + x6) / 2, y + h + 75, "Challenge: KI antwortet mit Belegen UND Gegenbelegen", ha="center", fontsize=10, color=ORANGE)
    for i, (txt, fuell, rand) in enumerate([("KI arbeitet allein", BLAU_HELL, BLAU), ("normaler Code, keine KI", GRAU_HELL, GRAU), ("Mensch entscheidet (Pflicht)", ORANGE_HELL, ORANGE)]):
        box(ax, 10 + i * 330, 420, 310, 44, txt, fuell, rand, size=11)
    ax.text(10, 495, "Jede KI-Aussage darf nur Beleg-IDs nennen, die wir ihr gegeben haben. Ein Test prüft das.", fontsize=10, color=GRAU)
    speichern(fig, "techflow")


def zitat_zu_requirement() -> None:
    fig, ax = neue_flaeche(1650, 460)
    ax.text(10, 28, "Vom Kundenzitat zur Entscheidung (Beispiel, vereinfacht)", fontsize=16, weight="bold", color=TEXT)
    karten = [
        ("1 Zitat · Beleg", "G60-0019 · USA · Wants\n\n\"Customer stated the center\nconsole layout is terrible. ...\nthe start/stop button being so\nclose to the other buttons\nmakes her nervous.\"", GRAU_HELL, GRAU),
        ("2 Befund", "Thema: Bedienung der\nMittelkonsole\n\nviele Kommentare,\nKonflikt mit 'Display gelobt'\n\nverweist auf Beleg-IDs", BLAU_HELL, BLAU),
        ("3 Anforderung", "Start/Stop ist nicht mit\nanderen Tasten zu\nverwechseln\n\nKriterium: Probandentest,\nZahl wird noch festgelegt\n\nAnnahme: Gewohnheit zählt", BLAU_HELL, BLAU),
        ("4 Priorität", "Score + Evidenzstufe\n\nWasserfall zeigt, wie viel\nSchmerz, Reichweite und\nWettbewerb beitragen", GRAU_HELL, GRAU),
        ("5 PM entscheidet", "Freigeben, ablehnen,\nbearbeiten, hinterfragen\n\nBegründung Pflicht\n\n→ Audit Trail", ORANGE_HELL, ORANGE),
    ]
    b, h, luecke, y = 300, 300, 30, 80
    for i, (titel, text, fuell, rand) in enumerate(karten):
        x = 10 + i * (b + luecke)
        box(ax, x, y, b, h, "", fuell, rand)
        ax.text(x + 14, y + 28, titel, fontsize=12, weight="bold", color=TEXT)
        ax.text(x + 14, y + 60, text, fontsize=9, color=TEXT, va="top", linespacing=1.45)
        if i < len(karten) - 1:
            pfeil(ax, x + b + 3, y + h / 2, x + b + luecke - 3, y + h / 2)
    ax.text(10, 420, "Ziel für die App: von jeder Anforderung per Klick zurück bis zum Originalkommentar.", fontsize=11, color=GRAU)
    speichern(fig, "zitat_zu_requirement")


def kopf(ax, titel: str, breite: int) -> None:
    box(ax, 0, 0, breite, 56, "", "white", GRAU_HELL)
    ax.text(20, 28, "Signal2Spec", fontsize=13, weight="bold", color=BLAU, va="center")
    for i, name in enumerate(["Anforderungen", "Trichter", "Audit Trail"]):
        aktiv = name == titel
        ax.text(220 + i * 170, 28, name, fontsize=10, va="center", color=BLAU if aktiv else GRAU, weight="bold" if aktiv else "normal")
    box(ax, breite - 190, 12, 170, 32, "Szenario: G60-US  ▾", "white", GRAU, size=9)


def evidenz_badge(ax, x, y, stufe: str) -> None:
    farbe = {"A": GRUEN, "B": "#7FB069", "C": GELB, "D": ROT}[stufe]
    box(ax, x, y, 26, 22, stufe, farbe, farbe, size=9, fett=True, farbe="white")


def mockup_liste() -> None:
    fig, ax = neue_flaeche(1100, 560)
    kopf(ax, "Anforderungen", 1100)
    ax.text(20, 84, "Priorisierte Anforderungen · Beispielwerte, nicht echt", fontsize=11, weight="bold", color=TEXT)
    spalten = [(20, "Rang"), (80, "Anforderung"), (520, "Score"), (700, "Evidenz"), (790, "Konflikt"), (880, "Status")]
    for x, t in spalten:
        ax.text(x, 118, t, fontsize=9, color=GRAU)
    zeilen = [("1", "Physische Bedienelemente für Top-Funktionen", 82, "A", "ja", "proposed"),
              ("2", "Tasten gegen Verwechslung absichern", 74, "B", "–", "proposed"),
              ("3", "Ladeplanung ohne App-Wechsel", 69, "B", "–", "approved"),
              ("4", "Sitzkomfort auf Langstrecke", 61, "C", "ja", "proposed"),
              ("5", "Smartphone-Anbindung ohne Abbrüche", 55, "C", "–", "rejected")]
    for i, (r, t, s, e, k, st) in enumerate(zeilen):
        y = 135 + i * 72
        box(ax, 10, y, 1080, 60, "", "white", GRAU_HELL)
        ax.text(30, y + 30, r, fontsize=12, weight="bold", va="center", color=TEXT)
        ax.text(80, y + 30, t, fontsize=11, va="center", color=TEXT)
        box(ax, 520, y + 24, 140, 10, "", GRAU_HELL, GRAU_HELL)
        box(ax, 520, y + 24, 140 * s / 100, 10, "", BLAU, BLAU)
        ax.text(670, y + 30, str(s), fontsize=10, va="center", color=TEXT)
        evidenz_badge(ax, 710, y + 19, e)
        ax.text(795, y + 30, k, fontsize=10, va="center", color=ORANGE if k == "ja" else GRAU)
        ax.text(880, y + 30, st, fontsize=10, va="center", color=TEXT)
    speichern(fig, "mockup_1_liste")


def mockup_detail() -> None:
    fig, ax = neue_flaeche(1100, 700)
    kopf(ax, "Anforderungen", 1100)
    ax.text(20, 84, "REQ-001 · Physische Bedienelemente für Top-Funktionen", fontsize=13, weight="bold", color=TEXT)
    evidenz_badge(ax, 880, 72, "A")
    ax.text(915, 84, "Status: proposed", fontsize=9, va="center", color=GRAU)
    box(ax, 20, 110, 330, 330, "", "white", GRAU_HELL)
    ax.text(34, 132, "Beschreibung", fontsize=10, weight="bold", color=TEXT)
    ax.text(34, 150, "Lautstärke, Klima und Defrost\nsind ohne Blick auf den Bildschirm\nbedienbar.", fontsize=9.5, va="top", color=TEXT)
    ax.text(34, 225, "Messkriterium", fontsize=10, weight="bold", color=TEXT)
    ax.text(34, 243, "Jede Funktion in einem Handgriff,\nim Test >= 80 % blind bedienbar.", fontsize=9.5, va="top", color=TEXT)
    ax.text(34, 305, "Annahmen / Unsicherheit", fontsize=10, weight="bold", color=ORANGE)
    ax.text(34, 323, "• Sprachsteuerung könnte den\n  Bedarf bis 2030 senken.\n• Gilt für den US-Markt.", fontsize=9.5, va="top", color=TEXT)
    box(ax, 370, 110, 330, 330, "", "white", GRAU_HELL)
    ax.text(384, 132, "Score-Aufschlüsselung", fontsize=10, weight="bold", color=TEXT)
    faktoren = [("Kundenschmerz", 22), ("Reichweite", 16), ("Zufriedenh.-Lücke", 14), ("Wettbewerb", 12), ("Zukunft", 8), ("Aufwand", 10)]
    for i, (n, v) in enumerate(faktoren):
        y = 160 + i * 40
        ax.text(384, y, n, fontsize=9.5, va="center", color=TEXT)
        box(ax, 540, y - 7, 130 * v / 22, 14, "", BLAU, BLAU)
        ax.text(545 + 130 * v / 22, y, f"+{v}", fontsize=9, va="center", color=TEXT)
    ax.text(384, 410, "Summe 82 × Evidenzfaktor A (1,0) = Score 82", fontsize=9.5, color=GRAU)
    box(ax, 720, 110, 360, 330, "", "white", GRAU_HELL)
    ax.text(734, 132, "Kundenstimmen und Quellen", fontsize=10, weight="bold", color=TEXT)
    ax.text(734, 150, "\"... start/stop button so close to\nthe other buttons makes her nervous.\"\n— G60-0019 · USA", fontsize=9.5, va="top", color=TEXT, style="italic")
    ax.text(734, 230, "Studie: Beispielwert unzufrieden", fontsize=9.5, color=TEXT)
    ax.text(734, 255, "Web: 3 Quellen (high / medium)", fontsize=9.5, color=TEXT)
    ax.text(734, 280, "Gegenbeleg: Display wird gelobt", fontsize=9.5, color=ORANGE)
    box(ax, 20, 460, 1060, 60, "Begründung (Pflicht): ______________________________________________", "white", GRAU, size=10, ha="left")
    for i, (n, f) in enumerate([("Freigeben", GRUEN), ("Ablehnen", ROT), ("Bearbeiten", GRAU), ("Hinterfragen", BLAU)]):
        box(ax, 20 + i * 150, 545, 135, 40, n, f, f, size=10, fett=True, farbe="white")
    ax.text(20, 620, "Beispielwerte. Score 82 entspricht Rang 1 im Listen-Mockup.", fontsize=9, color=GRAU)
    speichern(fig, "mockup_2_detail")


def mockup_audit() -> None:
    fig, ax = neue_flaeche(1100, 520)
    kopf(ax, "Audit Trail", 1100)
    ax.text(20, 84, "Audit Trail · Beispieleinträge", fontsize=12, weight="bold", color=TEXT)
    box(ax, 800, 68, 280, 32, "Kette gültig ✓  (verify)", "#DFF3E8", GRUEN, size=10, fett=True, farbe=GRUEN)
    ereignisse = [("REQUIREMENT_PROPOSED", "System", "Vorschlag aus 3 Befunden", "a91f…"),
                  ("PM_CHALLENGED", "PM", "Ist das nur Gewohnheit?", "7c02…"),
                  ("PM_EDITED", "PM", "Kriterium auf 80 % präzisiert", "e5b8…"),
                  ("PM_APPROVED", "PM", "Belege reichen, Annahme akzeptiert", "30d4…"),
                  ("WEIGHTS_CHANGED", "PM", "Zukunft von 10 auf 20 %", "bb17…")]
    for i, (typ, wer, warum, h) in enumerate(ereignisse):
        y = 125 + i * 72
        box(ax, 10, y, 1080, 58, "", "white", GRAU_HELL)
        ax.text(26, y + 22, typ, fontsize=10, weight="bold", color=BLAU)
        ax.text(26, y + 42, f"{wer} · {warum}", fontsize=9.5, color=TEXT)
        ax.text(1000, y + 30, f"hash {h}", fontsize=9, color=GRAU, va="center", ha="center")
        if i < len(ereignisse) - 1:
            pfeil(ax, 1000, y + 52, 1000, y + 78)
    ax.text(20, 495, "Jeder Eintrag enthält den Hash des vorherigen. Wer etwas ändert, bricht die Kette.", fontsize=9, color=GRAU)
    speichern(fig, "mockup_3_audit")


if __name__ == "__main__":
    techflow()
    zitat_zu_requirement()
    mockup_liste()
    mockup_detail()
    mockup_audit()
