# Tech-Partner: OpenAI und Entire

## OpenAI

### Credits

- 75 USD API-Credits pro Person (Event-Guide), also ~375 USD fürs Team.
- Verteilung: Die EHL-Plattform verschickt **Einmal-Codes pro Person per E-Mail** (`tum-ai/ehl` `lib/credit-codes.ts:1-8`: „one-per-person sponsor credit codes … single-use and non-recoverable once sent“). Einlösen auf platform.openai.com unter Billing. **UNBESTÄTIGT**, ob vorab oder vor Ort.

### Welche APIs sich für 24 h lohnen

| Baustein | Wofür | Empfehlung |
|---|---|---|
| **Responses API** | Standard-Aufruf für Text, Tools, Dateien | **Ja**, das ist OpenAIs empfohlener Weg; die Assistants API läuft aus |
| **Structured Outputs** (JSON-Schema/Pydantic) | Daten zuverlässig aus Dokumenten ziehen | **Ja, Kernbaustein**: Das LLM liest, unser Python-Code rechnet |
| **Embeddings** | Suche/Abgleich in Katalogen, Clustering | Ja, wenn wir suchen oder gruppieren müssen |
| **File inputs / Vision** | PDFs und Bilder direkt ans Modell | Ja, für Angebots-PDFs, Zeichnungen, Fotos |
| **Agents SDK** | mehrstufige Agenten mit Tools und Übergaben | Nur, wenn die Challenge echte Mehrschritt-Agenten verlangt; sonst eine einfache Python-Schleife (leichter zu erklären) |
| **Realtime API** | Sprache in Echtzeit | Nur bei Sprach-Use-Case |
| **Codex** | Coding-Agent | Wir nutzen Claude Code; Codex-Talk Sa 15:00 lohnt sich trotzdem |

### Modelle

Die aktuellen Modellnamen und Preise widersprechen sich zwischen den Quellen (Drittanbieter-Preisseiten, Oktober 2026). Deshalb **UNBESTÄTIGT**, Samstag prüfen:

```bash
python -c "from openai import OpenAI; print(sorted(m.id for m in OpenAI().models.list().data))"
```

Faustregel: **kleines/günstiges Modell** für Massen-Extraktion und Tests, **großes Modell** nur für die eine schwierige Entscheidung. Modellname in `.env` (`OPENAI_MODEL`), nie hart im Code.

### Credits sinnvoll verbrauchen

1. **Entwicklung:** Jede Person nutzt ihren eigenen Key lokal in `.env`.
2. **Deployte Demo:** genau **ein** Key (Piyush) in den Umgebungsvariablen von Render/Vercel.
3. Im OpenAI-Dashboard pro Projekt ein **Budget-Limit** setzen (z. B. 60 USD), damit eine Endlosschleife nicht alles frisst.
4. **Antworten cachen** (Hash von Prompt + Eingabe → Datei in `demo/cache/`). Das spart Geld und macht die Demo reproduzierbar.
5. Evaluation über ein kleines Testset (20-50 Fälle) zuerst mit dem kleinen Modell.

### Keys sicher verteilen

- **Nie** Keys in Discord, WhatsApp, Screenshots oder Commits. Das Repo ist öffentlich, und Bots finden Keys in Minuten.
- Jeder erzeugt seinen eigenen Key auf platform.openai.com → API keys, trägt ihn in `.env` ein (Vorlage `.env.example`).
- Geleakt? **Sofort widerrufen** (Dashboard → Revoke), neuen Key erzeugen, dann Piyush Bescheid geben. `python scripts/secret_scan.py` prüft vor jedem PR.

## Entire

### Was Entire macht

Entire zeichnet die Sessions unserer KI-Agenten auf: Prompts, Transcript und berührte Dateien. Bei jedem Commit entsteht ein **Checkpoint**, der mit dem Commit verknüpft ist (Trailer `Entire-Checkpoint: <ID>`). Beim `git push` werden die Checkpoints als eigene Git-Refs (`refs/entire/checkpoints/<xx>/<ID>`) mitgeschickt (docs.entire.io/cli/checkpoints). **Ohne Checkpoints nimmt die EHL keine Abgabe an** (Event-Guide; `tum-ai/ehl` `lib/submission-snapshots/prepare.ts:167-178`).

### Installation (offiziell, docs.entire.io/cli/installation)

| System | Befehl |
|---|---|
| Windows (PowerShell) | `irm https://entire.io/install.ps1 \| iex` → installiert nach `%USERPROFILE%\.local\bin` und trägt das in den PATH ein. **Terminal danach neu öffnen.** |
| Windows (Scoop) | `scoop bucket add entire https://github.com/entireio/scoop-bucket.git` dann `scoop install entire/entire` |
| macOS | `brew install --cask entireio/tap/entire` (oder `curl -fsSL https://entire.io/install.sh \| bash`) |
| Linux | `curl -fsSL https://entire.io/install.sh \| bash` → `~/.local/bin` muss im PATH sein |

Prüfen: `entire version` (bei uns getestet: 0.11.4).

### Im Repo aktivieren (jede Person, einmal nach dem Klonen)

```bash
entire enable --agent claude-code
entire status
```

Warum jede Person: Die Git-Hooks liegen in `.git/hooks/` und werden **nicht** mitgeklont. Die Claude-Hooks (`.claude/settings.json`) und die Team-Einstellungen (`.entire/settings.json`) sind dagegen schon im Repo.

### Unsere Team-Einstellungen (`.entire/settings.json`)

- `"commit_linking": "always"`: Entire verknüpft jeden Commit automatisch mit der Session. **Warum:** Ohne diese Einstellung fragt Entire bei jedem Commit interaktiv „Link this commit to session context? [Y/n/a]“. Wenn Claude Code committet, gibt es niemanden, der antwortet, und **der Commit hängt für immer**. Das ist uns am 09.10. passiert; mit der Einstellung dauert der Hook 1 Sekunde (docs.entire.io/guides/checkpoints/capture-checkpoints).
- `"checkpoints": {"primary": {"type": "git-refs"}}`: aktuelles Ref-Format, das die EHL zuerst sucht (`lib/entire.ts:41-55`).

### Best Practices für 5 Leute mit je einem Agenten

1. **Committen, während die Claude-Session läuft.** Nur dann enthält der Checkpoint Prompts.
2. **Regelmäßig pushen** (mindestens alle 1-2 Stunden). Die Checkpoints gehen mit jedem `git push` mit; die Ausgabe zeigt `[entire] Pushing N checkpoint ref(s) to origin… done`.
3. **Nicht aus GUI-Programmen committen** (GitHub Desktop, VS-Code-Button). Dort laufen die Hooks evtl. nicht (docs.entire.io troubleshooting). Wenn doch nötig: `entire configure --absolute-git-hook-path`.
4. **Ownership-Sprache in jedem Prompt.** Der EHL-Session-Reviewer bewertet einen praktisch zufälligen Checkpoint ([EHL-BEWERTUNG.md](EHL-BEWERTUNG.md) Abschnitt 6).
5. **Git-E-Mail = GitHub-E-Mail** (`git config user.email`), sonst „Unknown author“ auf entire.io.
6. Prüfen, ob alles auf GitHub ist: `git ls-remote origin 'refs/entire/checkpoints/*'`.
7. Probleme: `entire status`, dann `entire doctor`. Hängende Sessions: `entire session stop --all`.
8. **Nie `--no-verify`** beim Commit. Das überspringt die Entire-Hooks; unser Git-Schutz-Hook blockiert es.
9. Entire-Onboarding Sa 11:00-11:30 besuchen (mindestens eine Person, am besten Piyush).

### Nützliche Befehle

| Befehl | Was er tut |
|---|---|
| `entire status` | Ist Entire aktiv, welche Sessions laufen? |
| `entire checkpoint list` | Checkpoints auf diesem Rechner |
| `entire why <datei>:<zeile>` | Welcher Prompt hat diese Zeile erzeugt? (gut für Jury-Fragen) |
| `entire recap` | Zusammenfassung der letzten Agent-Arbeit |
| `entire doctor` | Repariert hängende Sessions und Metadaten |
