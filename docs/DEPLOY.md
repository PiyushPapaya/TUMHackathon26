# Deployment und Demo-Start

Kurz: **Frontend auf Vercel**, **Backend auf Render** (beide automatisch aus GitHub `main`).
Die Pipeline-Ergebnisse (`data/processed/`) liegen seit der Freigabe der Orga im Repo (die BMW-Rohdaten nicht),
darum kann Render das Backend direkt aus dem Repo starten. Lokal (A) bleibt das Netz für die Jury-Demo.

## A) Lokal in einem Befehl (für Jury-Demo und Probe)

```bash
bash scripts/start_demo.sh        # Mac, Linux, Git-Bash auf Windows
```

Das Skript startet das Backend auf `:8000`, baut das Frontend als Produktions-Build und startet es auf `:3000`.
Auf Windows ohne Git-Bash: zwei Terminals.

```powershell
python -m uvicorn main:app --app-dir src/backend --port 8000
cd src/frontend; npm ci; npm run build; npx next start -p 3000
```

Voraussetzung: `.env` aus `.env.example` kopiert, `data/processed/` vorhanden (Pipeline gelaufen oder von Piyush bekommen).
Ohne OpenAI-Key: `DEMO_MODUS=true` in `.env` (Antworten kommen aus `data/demo_cache/`, Prompt-Linse arbeitet dann mit Regeln).

## B) Online: Backend auf Render, Frontend auf Vercel

**Warum zwei Dienste:** Das Backend hält PM-Status im RAM und schreibt `audit.db`. Das braucht einen Prozess, der
dauerhaft läuft (`core/single_process.py`). Vercel-Funktionen starten ständig neu, dabei gingen Entscheidungen und
Prüfpfad verloren. Verworfen: FastAPI als Vercel-Funktion (Zustand bricht) und fest eingebaute Daten in der UI
(Entscheiden, Gewichte, Linse gingen nicht mehr).

**Schritt 1: Backend (zuerst, weil Vercel dessen Adresse braucht)**
1. render.com → *New* → *Blueprint* → GitHub-Repo wählen. Render liest `render.yaml` im Root.
2. Nach `OPENAI_API_KEY` gefragt: eigenen Key eintragen (oder leer lassen und `DEMO_MODUS` auf `true` stellen,
   dann kostet nichts, freie Fragen an den Assistenten gehen aber nicht).
3. Warten bis „Live“, dann `https://respec-api.onrender.com/health` öffnen (Name kann abweichen) → `"status":"ok"` und 6 Szenarien.

**Schritt 2: Frontend**
1. vercel.com → *Add New Project* → GitHub-Repo wählen.
2. **Root Directory:** `src/frontend` (wichtig, sonst findet Vercel kein Next.js). Rest bleibt automatisch.
3. **Environment Variable:** `NEXT_PUBLIC_API_URL` = Render-Adresse **ohne `/` am Ende**, z. B. `https://respec-api.onrender.com`.
   Gilt für Production und Preview. Die Variable landet im Browser, also nie einen Key eintragen.
4. Deploy. CORS ist schon offen für alle `*.vercel.app`-Adressen (`CORS_ORIGIN_REGEX` in `render.yaml`).
   Eigene Domain? Dann in Render bei `CORS_ORIGINS` ergänzen.
5. `NEXT_PUBLIC_API_URL` wird beim Build eingebacken: nach einer Änderung in Vercel **Redeploy** klicken.

**Wissen für die Demo**
- Gratis-Render schläft nach 15 Minuten ohne Aufruf. Der erste Aufruf danach dauert ca. 50 s.
  **Vor Pitch und Jury-Zeit einmal `/health` öffnen.**
- Nach Schlaf oder neuem Deploy ist `audit.db` leer (Render-Disk ist flüchtig). Die Pipeline-Daten bleiben, nur
  PM-Entscheidungen aus der Online-Version verschwinden. Für die Jury ist das gewollt: Jeder startet sauber.
- Öffentlicher Link + echter Key = Fremde können Credits verbrauchen. Beim OpenAI-Key ein Ausgabelimit setzen.
- Jeder Push auf `main` deployt beide automatisch. Rote CI heißt also auch: kaputte Online-Version.

## C) Ersatz: Backend über einen Tunnel vom Laptop

Falls Render ausfällt: Das Backend läuft auf dem Laptop, und ein Tunnel gibt ihm eine https-Adresse:

```bash
cloudflared tunnel --url http://localhost:8000     # oder: ngrok http 8000
```

Die ausgegebene `https://...`-Adresse kommt als `NEXT_PUBLIC_API_URL` in Vercel (danach neu deployen) und in `CORS_ORIGINS`.
Nachteil: Der Laptop muss während der Jury-Zeit laufen. Darum bleibt **A) lokal** der sichere Weg und B) ist die Zugabe.

## D) Medien

- Bilder liegen in `src/frontend/public/media/` (`poster.jpg`, `split.jpg`, `scenarios/<ID>.jpg`). Fehlende Dateien sind kein Fehler.
- Auto-Video: `bash scripts/make_frames.sh pfad/zum/v2.mp4` schreibt die Frames nach `public/media/car/`. Ziel höchstens 8 MB.
- Die Medien-Liste entsteht beim Build. Nach neuen Dateien also neu bauen.
- Achtung Vercel: `/media-manifest` liest `public/media/car/manifest.json` zur Laufzeit. Vercel-Funktionen sehen
  `public/` nicht, dann greift still die Fallback-Szene. Solange `car/` leer ist, ändert das nichts.

## E) Checkliste vor jedem Deploy

```bash
cd src/frontend && npm run lint && npm run build     # grün
python scripts/secret_scan.py                        # keine Keys
```

Danach im Browser: `/`, `/cockpit`, `/overview`, `/insights`, `/portfolio`, `/evidence`, `/audit`, `/guide` laden, Konsole ohne Fehler,
im Cockpit eine Gewichtung anwenden (Toast „WEIGHTS_CHANGED recorded“). Skill `demo-check` führt das gesamte Programm aus.
