# Glossar für Nicht-Coder

Kurz und ohne Fachchinesisch. Wenn ein Wort fehlt: Claude fragen („Erklär mir X in 2 Sätzen“) und hier ergänzen.

## Git und GitHub

| Wort | Bedeutung |
|---|---|
| **Repo (Repository)** | Der Projektordner mit allen Dateien und ihrer ganzen Geschichte. Unseres liegt auf GitHub. |
| **clone** | Das Repo einmalig von GitHub auf den eigenen Rechner kopieren. |
| **pull** | Die neuesten Änderungen der anderen von GitHub holen. |
| **commit** | Einen Zwischenstand mit kurzer Beschreibung speichern (nur auf deinem Rechner). |
| **push** | Deine Commits zu GitHub schicken, damit andere sie sehen. |
| **Branch** | Eine eigene Arbeitskopie. Du arbeitest auf `<vorname>/<thema>`, nie auf `main`. |
| **main** | Der Haupt-Branch. Was hier liegt, wird bei der Abgabe bewertet. Nur Piyush merged hierhin. |
| **Pull Request (PR)** | Die Bitte „prüft meine Änderungen und übernehmt sie in main“. |
| **merge** | Zwei Stände zusammenführen. |
| **Merge-Konflikt** | Zwei Personen haben dieselbe Stelle geändert; ein Mensch muss entscheiden. **Nie raten, Piyush holen.** |
| **Ruleset** | GitHub-Regel, die `main` schützt: nur per PR, nur Piyush darf mergen, CI muss grün sein. |
| **CODEOWNERS** | Datei, die festlegt, wer Änderungen in welchem Ordner freigeben muss. |
| **CI** | Automatische Prüfung bei jedem PR (Tests, Secret-Scan). Grüner Haken = alles ok. |
| **Trailer** | Zusatzzeile am Ende einer Commit-Nachricht, z. B. `Entire-Checkpoint: …`. |

## Unser Produkt und die Technik

| Wort | Bedeutung |
|---|---|
| **Frontend** | Was man im Browser sieht (bei uns Next.js in `src/frontend/`). |
| **Backend** | Der Server, der rechnet und das KI-Modell fragt (bei uns FastAPI in `src/backend/`). |
| **API** | Die „Speisekarte“ des Backends: Welche Anfrage bekommt welche Antwort. |
| **Endpunkt** | Ein einzelner Eintrag der API, z. B. `POST /analyse`. |
| **API-Vertrag** | Abmachung zwischen Frontend und Backend, wie Anfragen und Antworten aussehen (`src/shared/API.md`). |
| **Mock** | Eine Attrappe mit Beispieldaten, damit das Frontend schon arbeiten kann, bevor das Backend fertig ist. |
| **JSON** | Textformat für Daten: `{"name": "Lasse", "rolle": "Frontend"}`. |
| **LLM** | Großes Sprachmodell (z. B. von OpenAI), das Text liest und schreibt. |
| **Prompt** | Die Anweisung an ein LLM oder an Claude. |
| **Structured Outputs** | Das LLM muss in einem festen JSON-Format antworten, damit unser Code die Antwort sicher weiterverarbeiten kann. |
| **Embedding** | Ein Text als Zahlenliste, damit der Computer Ähnlichkeit messen kann (für Suche). |
| **Agent** | Ein LLM, das selbst Werkzeuge benutzt (suchen, rechnen, Dateien lesen) und mehrere Schritte macht. |
| **API-Key** | Geheimes Passwort für einen Dienst (z. B. OpenAI). Gehört in `.env`, **nie** ins Repo. |
| **.env** | Datei mit deinen Geheimnissen, nur auf deinem Rechner. `.env.example` ist die leere Vorlage. |
| **Dependency** | Fremde Software, die unser Code braucht (z. B. `fastapi`). Neue nur nach Rückfrage bei Piyush. |
| **Deploy** | Die App ins Internet stellen (Vercel, Render). |
| **Lint** | Automatische Prüfung auf Stil- und Flüchtigkeitsfehler im Code. |
| **Test** | Kleines Programm, das prüft, ob unser Code das Richtige tut. |

## Hackathon und Bewertung

| Wort | Bedeutung |
|---|---|
| **EHL** | European Hackathon League; ehl.gg ist die Plattform für Challenge-Wahl und Abgabe. |
| **Challenge** | Die Aufgabe eines Partners (BMW, Atira oder tacto). Der Captain wählt bis Sa 13:00. |
| **Deep Dive** | Vertiefung durch den Partner (Sa 12:00). Hier stellen wir unsere vorbereiteten Fragen. |
| **Report Card** | Der KI-Bericht über unser Repo, den die Jury liest. |
| **Snapshot / frozen_sha** | Der Commit auf `main`, der beim Klick auf „Submit“ eingefroren und bewertet wird. |
| **Entire** | Werkzeug, das unsere Claude-Sessions aufzeichnet. Pflicht für die Abgabe. |
| **Checkpoint** | Ein Entire-Eintrag pro Commit mit den Prompts dazu. |
| **Ownership-Sprache** | „Wir nehmen X, weil …; Y verworfen, weil …“. So zeigen wir, dass wir entscheiden, nicht die KI. |
| **export-ignore** | Markierung in `.gitattributes`: Diese Ordner kommen nicht in den Abgabe-Snapshot (spart Review-Budget). |
| **Code-Freeze** | Ab So 10:30 kein neuer Code mehr, nur noch Fehlerbehebung und Abgabe. |
| **MVP** | Kleinste Version des Produkts, die den Kern-Nutzen zeigt. |
| **Baseline** | Der einfache Vergleichswert (z. B. „ohne unser Tool“), gegen den wir unsere Zahl messen. |
