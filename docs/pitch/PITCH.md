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

### Harte Taktung (Sekunden, Summe 360)

| Teil | Sek. | Sprecher | Übergabe-Satz |
|---|---|---|---|
| Hook | 20 | Fabian | „… genau das hat Dennis beim Partner gehört.“ |
| Problem | 30 | Dennis | „Lasse zeigt euch, wie das mit uns aussieht.“ |
| Demo | 100 | Lasse klickt, Piyush erzählt | „Wie gut ist das? Aditya.“ |
| Ergebnis | 30 | Aditya | „Wie das technisch geht, in einem Satz: Piyush.“ |
| Tech | 15 | Piyush | „Und was als Nächstes kommt: Fabian.“ |
| Ask | 15 | Fabian | „Danke, wir freuen uns auf eure Fragen.“ |
| **Fragen** | **150** | Partner/Nutzen: Dennis · Technik: Piyush · Zahl/Evaluation: Aditya · UI/Demo: Lasse · Vision/Team: Fabian | Bei 5:45 beendet Fabian höflich. |

Zeitwächter: Aditya hält das Handy mit Stoppuhr hoch, bei 3:00 ein Finger und bei 3:30 die Faust (= sofort zum Ask).

### Wenn die Demo hängt (auswendig, Piyush)

> „Während das Netz nachdenkt, zeigen wir euch dieselbe Strecke aus unserer Aufnahme. Gleiche Eingabe, gleiche Ausgabe.“

Dann sofort, **ohne zu debuggen**: nach 5 Sekunden ohne Reaktion → Offline-Modus-Tab (`DEMO_MODUS=true`) oder Backup-Video (Ebenen siehe `demo/README.md`). Nie länger als 10 Sekunden warten.

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
