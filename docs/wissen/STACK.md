# Stack-Entscheidung und Scaffold-Befehle für Samstag

## Entscheidung

**Wir nehmen Python/FastAPI fürs Backend und Next.js (TypeScript, Tailwind) fürs Frontend**, weil:

- **Python** die Sprache von Piyush und Dennis ist und 71 % der platzierten EHL-Teams Python-dominiert waren ([VERGANGENE-PROJEKTE.md](VERGANGENE-PROJEKTE.md)). PDF-Parsing, Pandas und das OpenAI-SDK sind dort am stärksten, und alle drei Partner arbeiten mit Dokumenten und Daten ([SPONSOREN.md](SPONSOREN.md)).
- **Next.js** mit Claude Code für Nicht-Coder gut funktioniert: Seiten sind einzelne Dateien, Claude kennt das Framework sehr gut, und Vercel deployt es mit einem Klick. Eine schöne UI hilft im 6-Minuten-Pitch.
- **FastAPI** die API-Dokumentation automatisch unter `/docs` erzeugt. Das ist unser Vertrag zwischen Frontend und Backend, und man kann sie in der Jury zeigen.

**Verworfen:**
- *Nur Next.js (API-Routes in TypeScript):* ein Deploy weniger, aber Piyush und Dennis sind in Python schneller, und Daten/ML-Bibliotheken fehlen.
- *Streamlit:* sehr schnell für Daten-Demos, aber schwer gut aussehen zu lassen und schwer in Frontend/Backend aufzuteilen. Bleibt **Plan B**, falls die Challenge reine Datenanalyse ist; dann Streamlit statt Next.js in `src/frontend/`.
- *Django:* zu viel Setup für 24 h.

## Wie der EHL-Reviewer den Stack erkennt (wichtig!)

- Frameworks erkennt er **nur** aus `package.json` und `requirements.txt` **im Repo-Root** (`tum-ai/ehl` `lib/code-review/ingest.ts:87, 104`).
- Deshalb liegt **`requirements.txt` im Root** (nicht in `src/backend/`). Dann wird FastAPI erkannt.
- Next.js liegt in `src/frontend/package.json` und taucht im Metadaten-Feld „Frameworks“ nicht auf. Der Reviewer liest die Datei trotzdem früh (jede `package.json` ist Priority-Datei) und nennt Next.js im Tech-Stack. Das nehmen wir hin. Eine Root-`package.json` nur für die Erkennung würde Versionen doppelt pflegen.

## Scaffold-Befehle (erst Samstag nach dem Challenge-Reveal!)

> Vorher kein Produkt-Code (Regel-Unsicherheit, siehe [EHL-BEWERTUNG.md](EHL-BEWERTUNG.md) Abschnitt 9).

### Backend (Piyush), ca. 10 Minuten

```bash
git switch main && git pull && git switch -c piyush/backend-geruest
python -m venv .venv
# Windows (PowerShell): .venv\Scripts\Activate.ps1     Mac: source .venv/bin/activate
```

`requirements.txt` im Root anlegen (Versionen am Samstag mit `pip index versions <paket>` prüfen und pinnen):

```text
fastapi
uvicorn[standard]
openai
pydantic
python-dotenv
pytest
httpx
```

```bash
pip install -r requirements.txt
```

`src/backend/main.py` mit `/health` und CORS für `http://localhost:3000`, dann:

```bash
uvicorn main:app --app-dir src/backend --reload --port 8000
# Test: http://localhost:8000/health und http://localhost:8000/docs
```

### Frontend (Lasse mit Claude Code), ca. 10 Minuten

```bash
git switch main && git pull && git switch -c lasse/frontend-geruest
npx create-next-app@latest src/frontend --typescript --eslint --tailwind --app --src-dir --import-alias "@/*" --use-npm --yes
cd src/frontend && npm run dev
# Test: http://localhost:3000
```

`create-next-app` erkennt das vorhandene Git-Repo und legt kein zweites an. Falls `--yes` nicht unterstützt wird: ohne `--yes` starten und alle Fragen mit Enter bestätigen.

### Vertrag (Piyush), bis Samstag 14:00

- `src/shared/API.md`: jeder Endpunkt mit Methode, Pfad, Beispiel-Request und Beispiel-Response.
- `src/shared/beispiele/*.json`: dieselben Beispiel-Responses als Dateien. Das Frontend baut zuerst gegen diese Mocks.
- Änderungen am Vertrag **nur per PR von Piyush**.

## Hosting für die Live-Demo

| Teil | Wo | Warum | Achtung |
|---|---|---|---|
| Frontend | Vercel (Root Directory `src/frontend`) | Push → Deploy automatisch, kostenlos | `NEXT_PUBLIC_API_URL` in Vercel setzen |
| Backend | Render (Web Service, Start: `uvicorn main:app --app-dir src/backend --host 0.0.0.0 --port $PORT`) | kostenlos, liest `requirements.txt` aus dem Root | Free-Tier schläft ein → 5 Minuten vor dem Pitch aufwecken |
| Backup | Laptop lokal + Backup-Video | Netz im Saal kann ausfallen | siehe [PITCH.md](../pitch/PITCH.md) |

Neue Hosting-Konten oder Dienste: vorher mit Piyush absprechen. Secrets nur in die Umgebungsvariablen des Dienstes, nie ins Repo.
