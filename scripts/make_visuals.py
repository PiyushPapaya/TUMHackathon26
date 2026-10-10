"""Erzeugt die Charts in visuals/charts/ aus den echten BMW-Rohdaten (data/raw/).

Aufruf aus dem Repo-Root:  python scripts/make_visuals.py
Warum ein Skript: Jede Person kann Farben, Titel oder Filter ändern und die Bilder neu bauen.
Die Charts zeigen nur Zähl- und Prozentwerte, keine einzelnen Kommentare.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "visuals" / "charts"
BLAU, GRAU, ROT, GRUEN = "#1C69D4", "#9AA4B2", "#D64545", "#2E9E6B"

plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})


def speichern(fig, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=150)
    plt.close(fig)
    print("geschrieben:", OUT / name)


def chart_beschwerden_g60_us() -> None:
    d = pd.read_excel(RAW / "G60_feedback_hackathon.xlsx")
    us = d[d["Country"] == "US"]
    # Likes sind keine Beschwerden. Wir zählen Defekte, Bedienprobleme und Wünsche.
    kritisch = us[(us["Feedback Type"] != "Likes") & (us["Vfc level2 Name"] != "no_class_found")]
    top = kritisch["Vfc level2 Name"].value_counts().head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(top.index, top.values, color=BLAU)
    fig.suptitle(f"G60 USA: häufigste Kritik-Themen ({len(kritisch)} Kommentare ohne Likes)", x=0.01, ha="left", fontsize=12)
    ax.set_xlabel("Anzahl Kommentare")
    speichern(fig, "01_top_beschwerden_g60_us.png")


def chart_feedback_typen() -> None:
    d = pd.read_excel(RAW / "G60_feedback_hackathon.xlsx")
    us = d[d["Country"] == "US"]
    teile = us["Feedback Type"].value_counts()
    farben = {"Likes": GRUEN, "Difficult to Use": ROT, "Wants": BLAU, "Defect": "#E0A030"}
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(teile.index, teile.values, color=[farben.get(i, GRAU) for i in teile.index])
    fig.suptitle(f"G60 USA: Was die {len(us)} Kommentare ausdrücken", x=0.01, ha="left", fontsize=12)
    ax.set_ylabel("Anzahl Kommentare")
    speichern(fig, "02_feedback_typen_g60_us.png")


def _studie_unzufrieden() -> pd.DataFrame:
    """Liest die US-Studie: je Attribut ein Block mit 7 Stufen. Unzufrieden = die 3 unteren Stufen."""
    s = pd.read_excel(RAW / "F70_G60_G68_G70_customer_studies.xlsx", sheet_name="US_2025", header=None)
    zeilen = []
    for i in range(len(s) - 9):
        if str(s.iloc[i + 1, 0]).strip() == "Sample total":
            unten = s.iloc[i + 2 : i + 5, [2, 3]].astype(float).sum()
            zeilen.append({"attribut": str(s.iloc[i, 0]).strip(), "G60": unten.iloc[0] * 100, "G70": unten.iloc[1] * 100})
    return pd.DataFrame(zeilen)


def chart_studie_g60_vs_g70() -> None:
    df = _studie_unzufrieden().sort_values("G60", ascending=False).head(10).iloc[::-1]
    y = range(len(df))
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.barh([i + 0.2 for i in y], df["G60"], height=0.4, color=BLAU, label="5er G60")
    ax.barh([i - 0.2 for i in y], df["G70"], height=0.4, color=GRAU, label="7er G70")
    ax.set_yticks(list(y))
    ax.set_yticklabels(df["attribut"])
    ax.set_xlabel("% unzufrieden (I Hate It / A Failure / Unsatisfactory)")
    fig.suptitle("US-Kundenstudie: die 10 schwächsten Attribute des G60 im Vergleich zum G70", x=0.01, ha="left", fontsize=12)
    ax.legend()
    speichern(fig, "03_studie_g60_vs_g70.png")


def chart_absatz() -> None:
    v = pd.read_excel(RAW / "sales_volumes.xlsx", sheet_name="G60_G68")
    x = range(len(v))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for versatz, spalte, farbe in [(-0.27, "volume_2024", GRAU), (0, "volume_2025", BLAU), (0.27, "volume_2030", GRUEN)]:
        ax.bar([i + versatz for i in x], v[spalte], width=0.27, color=farbe, label=spalte[-4:])
    ax.set_xticks(list(x))
    ax.set_xticklabels(v["market"])
    fig.suptitle("5er (G60/G68): Absatz pro Markt, 2024 / 2025 / Prognose 2030", x=0.01, ha="left", fontsize=12)
    ax.set_ylabel("Fahrzeuge")
    ax.legend()
    speichern(fig, "04_absatz_pro_markt.png")


if __name__ == "__main__":
    chart_beschwerden_g60_us()
    chart_feedback_typen()
    chart_studie_g60_vs_g70()
    chart_absatz()
