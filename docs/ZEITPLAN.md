# Zeitplan Sa 09:00 bis So 12:00 (pro Rolle)

Rollen: **P** = Piyush (Lead, Backend, Merges) · **L** = Lasse (Frontend) · **A** = Aditya (Daten, Tests, Demo) · **D** = Dennis (Partner-Kontakt, Research, README-Texte) · **F** = Fabian (Pitch, Slides, Design, Video)

**Harte Meilensteine** (fett) werden nicht verschoben, sondern der Umfang wird gekürzt.

## Samstag

| Zeit | Programm | P | L | A | D | F |
|---|---|---|---|---|---|---|
| 09:00 | Check-in (**alle**, sonst keine Challenge-Wahl) | Check-in, Laptop: `git pull`, `entire status` | dto. | dto. | dto. | dto. |
| 10:00 | Kick-off + Reveal | mitschreiben | mitschreiben | Daten-Hinweise notieren | **Briefs wörtlich mitschreiben** → `CHALLENGE.md` | Story-Ideen notieren |
| 11:00 | Entire-Onboarding | **hingehen** | Setup prüfen | Setup prüfen | Skill `challenge-intake` pro Partner | Skill `challenge-intake` mitlesen |
| 11:30 | Ideen-Scoring (30 min) | moderiert, entscheidet Stack-Schnitt | Machbarkeit Frontend | Messbarkeit: welche Zahl? | Scores eintragen | Demo-Fähigkeit bewerten |
| 12:00 | Deep Dives (parallel) | Favorit-Partner | Favorit-Partner | 2. Partner | **Fragen stellen** (aus SPONSOREN.md) | 3. Partner |
| **13:00** | **Idee fix + Challenge auf ehl.gg gewählt** | **wählt auf ehl.gg** | | | `CHALLENGE.md` final | One-Liner Entwurf |
| 13:30 | Hacking-Start | Backend-Gerüst (STACK.md) | Frontend-Gerüst | Testset/Daten sichten, 20 Fälle labeln | README-Problem/Lösung | Pitch-Gerüst, Logo |
| **14:00** | **API-Vertrag steht** (`src/shared/API.md` + Beispiel-JSON) | schreibt + merged | baut gegen Mocks | Testfälle als JSON | | Wireframe/Design |
| 15:00 | Talk: OpenAI Codex | (optional) | | | hingehen, Notizen | |
| 16:00 | Fireside Chat Atira | | | | hingehen (wenn Atira gewählt: Pflicht) | hingehen |
| 16:00-18:00 | Bauen | LLM-Pipeline | Kernseiten | Eval-Skript (Baseline) | Mentoren/Cherry Office Hours | Slides 1-5 |
| **18:00** | **Erster End-to-End-Durchstich** (UI → API → LLM → UI, hässlich ok) | | | erste Zahl gegen Baseline | Zahl in README | Demo-Ablauf skizzieren |
| 19:00 | Dinner (**gemeinsam, 20 min Stand-up**: was läuft, was kürzen?) | | | | | |
| 19:30-22:00 | Bauen | Robustheit, Fehlerfälle | UX der Demo-Strecke | Tests + Demo-Daten | Jury-FAQ | Slides + Story |
| **22:00** | **MVP läuft** (auf main, deployt), **erste Abgabe auf ehl.gg** (Sicherheitsnetz) | merged + submit | | Selbstreview-Skill | | |

## Nacht (Schlafschichten, je 4 h)

| Schicht | Schläft | Wach (Aufgabe) |
|---|---|---|
| 23:00-03:00 | **D, F** | P (Backend), L (Frontend), A (Eval) |
| 03:00-07:00 | **P, L, A** | D (README, Jury-FAQ), F (Slides, Video-Skript) |

Regel nachts: Nur kleine, getestete PRs. Piyush merged vor dem Schlafen alles Grüne. Nichts Neues anfangen nach 02:00.

## Sonntag

| Zeit | P | L | A | D | F |
|---|---|---|---|---|---|
| 07:00 | Merge-Runde, Deploy prüfen | Bugs aus Nacht | Eval final (Zahl + Konfidenz/Spanne) | README final | Slides final |
| **08:00** | **Feature-Freeze**: nur noch Bugs, Texte, Demo | | | | |
| 08:00 | Frühstück + Stand-up | | | | |
| 08:30-10:00 | Skill `demo-check` (Fresh Clone) | UI-Politur der Demo-Strecke | **Backup-Video aufnehmen** (2 min) | Skill `selbstreview`, Fixes priorisieren | Video schneiden + hochladen |
| **10:00** | **Pitch-Probe mit Stoppuhr** (Skill `pitch-prep`), alle 5 beantworten je 2 Jury-Fragen | | | | |
| **10:30** | **Code-Freeze** → Skill `abgabe` (Runbook [ABGABE.md](ABGABE.md)) | | | | |
| **11:30** | **Abgegeben** (30 min Puffer) | | | | |
| 12:00 | Deadline (hart) · danach Pitches 12:00-14:30, 6 min/Team | | | | |
| 14:30 | Finalisten · 16:30 Preisverleihung | | | | |

## Merge-Fenster (Piyush ist der einzige Merger)

| Tag | Fenster |
|---|---|
| Sa | **jede volle Stunde 14:00-24:00** (14, 15, … 23, 24 Uhr) |
| Nacht | nur nach Absprache (Vertretungsmodus, `docs/ABGABE.md` Notfall B) |
| So | **08:00, 09:00, 10:00, 10:30 (letzter Merge = Code-Freeze)** |

- Zum Fenster muss der PR **grün** sein (CI `checks`) und **aktuell mit main** (`git merge origin/main`, kein Rebase).
- PRs, die das Fenster verpassen oder rot sind, warten aufs nächste. Kein Hinterherrufen.
- Warum: Ein Merger für 5 Leute wird sonst zum Engpass und muss ständig den Kontext wechseln. Feste Takte machen Merges planbar.

## Timeboxing-Regeln

- Jede Aufgabe bekommt eine Zeitbox. **Nach 45 min festgefahren → Piyush/Team fragen**, nicht weiterbohren.
- Wenn ein harter Meilenstein wackelt: **Umfang kürzen**, nicht Zeit verlängern. Kürzungsreihenfolge steht in `CHALLENGE.md` (Nice-to-have zuerst).
- Stündlich: committen + pushen (Entire-Checkpoints!) + kleiner PR.
