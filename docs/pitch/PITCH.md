# Pitch: 6 Minuten inklusive Fragen (strikt)

> Owner: Fabian. Probe mit Stoppuhr: So 10:00 (Skill `pitch-prep`).
> Pitches laufen So 12:00-14:30 parallel pro Challenge, Reihenfolge zufällig.
> Die Jury hat unser Pitch-Deck schon eingebettet vor sich (EHL-Plattform) und den KI-Report gelesen.

## Zeitplan der 6 Minuten

| Zeit | Block | Wer | Inhalt |
|---|---|---|---|
| 0:00-0:20 | **Hook** | Fabian | Ein Satz, den man fühlt: konkrete Person, konkreter Schmerz, eine Zahl. |
| 0:20-0:50 | **Problem** | Dennis | Wer, wie oft, was kostet es heute? (Zahl vom Partner oder aus dem Brief, Quelle nennen) |
| 0:50-2:30 | **Live-Demo des Kernflows** | Lasse (klickt) + Piyush (erzählt) | Genau **ein** Durchlauf: Eingabe → Ergebnis → Begründung. Keine Menüs, keine Einstellungen. |
| 2:30-3:00 | **Ergebnis / Metrik** | Aditya | „Auf N Testfällen: X statt Y (Baseline).“ Eine Folie, eine Zahl, Messmethode in einem Satz. |
| 3:00-3:15 | **Tech in einem Satz** | Piyush | „Das LLM liest, unser Code entscheidet: Structured Outputs → Python-Regeln → Begründung mit Belegstelle.“ |
| 3:15-3:30 | **Ask / Nächster Schritt** | Fabian | Was wir mit dem Partner als Nächstes testen würden. |
| 3:30-6:00 | **Fragen** | alle | Antwort-Gerüste in [JURY-FAQ.md](JURY-FAQ.md). Wer gefragt wird, antwortet; Piyush ergänzt nur Technik. |

Faustregel: **Wenn die Probe länger als 3:30 dauert, fliegt Inhalt raus, nicht Tempo rein.**

## Folien (maximal 6, als PDF exportieren, ist Pflichtfeld bei der Abgabe)

1. Titel: Projektname, One-Liner, Team, Challenge
2. Problem mit Zahl
3. (Demo läuft live, Folie nur als Fallback-Screenshot)
4. Ergebnis: Zahl vs. Baseline, Messmethode, ehrliche Grenze
5. So funktioniert's: das Mermaid-Bild aus der README als Grafik
6. Nächster Schritt / Ask

## Demo-Drehbuch (Lasse + Aditya)

| Schritt | Klick | Was man sieht | Was Piyush sagt |
|---|---|---|---|
| 1 | Demo-Datei aus `demo/` laden | Eingabe | „Das ist eine echte Anfrage aus dem Partner-Datensatz.“ |
| 2 | „Analysieren“ | Ladeanzeige (< 10 s, sonst Cache) | „Jetzt extrahiert das Modell …“ |
| 3 | Ergebnis | Tabelle/Karte + Begründung | „Jede Aussage hat eine Belegstelle.“ |
| 4 | Detail aufklappen | Belegstelle im Original | „Darum kann der Nutzer uns vertrauen.“ |

## Demo-Ausfallplan (wird geprobt!)

| Was fällt aus | Plan |
|---|---|
| WLAN im Saal | Hotspot vom Handy (vorher testen); Backend lokal auf dem Laptop |
| Deployte URL / Render schläft | 5 min vorher aufwecken; sonst lokal: `uvicorn …` + `npm run dev` |
| OpenAI langsam/down | **Demo-Modus mit Cache** (`demo/cache/`), gleiche Eingabe = gleiche Antwort |
| Laptop | zweiter Laptop mit fertigem Setup (Aditya) |
| Alles | **Backup-Video** (2 min, Link in README und auf dem Desktop), Ton aus, live kommentieren |

## Checkliste vor dem Pitch (So 11:45)

- [ ] Laptop am Strom, Bildschirm-Spiegelung getestet, Benachrichtigungen aus
- [ ] Demo-Tab offen, Demo-Datei griffbereit, Backup-Video lokal gespeichert
- [ ] Backend aufgeweckt
- [ ] Jede Person kann das Produkt in 2 Sätzen erklären (siehe `team/<name>.md`)
