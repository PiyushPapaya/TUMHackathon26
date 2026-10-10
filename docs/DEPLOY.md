# Deployment und Demo-Start

Kurz: **Frontend** lässt sich auf Vercel/Netlify veröffentlichen, das **Backend läuft bei uns lokal**,
weil die Pipeline-Ergebnisse (`data/processed/`) aus BMW-Daten entstehen und nie ins Repo dürfen (siehe `data/README.md`).

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

## B) Frontend auf Vercel (öffentlicher Link)

1. Vercel → *Add New Project* → dieses GitHub-Repo wählen.
2. **Root Directory:** `src/frontend`. Framework wird als Next.js erkannt, Build-Befehl bleibt `next build`.
3. **Environment Variable:** `NEXT_PUBLIC_API_URL` = öffentliche Adresse des Backends (siehe C).
   Die Variable landet im Browser, also nie einen Key eintragen.
4. Backend `.env`: `CORS_ORIGINS=https://<dein-projekt>.vercel.app,http://localhost:3000` setzen, sonst blockt der Browser die Anfragen.
5. Deploy. Die Startseite funktioniert auch ohne Backend (Zahlen zeigen dann „–“), die Cockpit-Seiten brauchen es.

## C) Backend öffentlich erreichbar machen, ohne Daten hochzuladen

Das Backend bleibt auf dem Laptop, ein Tunnel gibt ihm eine https-Adresse:

```bash
cloudflared tunnel --url http://localhost:8000     # oder: ngrok http 8000
```

Die ausgegebene `https://...`-Adresse kommt als `NEXT_PUBLIC_API_URL` in Vercel (danach neu deployen) und in `CORS_ORIGINS`.
Nachteil: Der Laptop muss während der Jury-Zeit laufen. Darum bleibt **A) lokal** der sichere Weg und B) ist die Zugabe.

## D) Medien

- Bilder liegen in `src/frontend/public/media/` (`poster.jpg`, `split.jpg`, `scenarios/<ID>.jpg`). Fehlende Dateien sind kein Fehler.
- Auto-Video: `bash scripts/make_frames.sh pfad/zum/v2.mp4` schreibt die Frames nach `public/media/car/`. Ziel höchstens 8 MB.
- Die Medien-Liste entsteht beim Build. Nach neuen Dateien also neu bauen.

## E) Checkliste vor jedem Deploy

```bash
cd src/frontend && npm run lint && npm run build     # grün
python scripts/secret_scan.py                        # keine Keys
```

Danach im Browser: `/`, `/cockpit`, `/overview`, `/insights`, `/portfolio`, `/evidence`, `/audit`, `/guide` laden, Konsole ohne Fehler,
im Cockpit eine Gewichtung anwenden (Toast „WEIGHTS_CHANGED recorded“). Skill `demo-check` führt das gesamte Programm aus.
