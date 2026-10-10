#!/usr/bin/env bash
# Startet die komplette Demo lokal: Backend (Port 8000) und das Frontend als schneller Produktions-Build (Port 3000).
# Warum Produktions-Build: Er ist deutlich schneller als "npm run dev" und zeigt genau das, was die Jury sieht.
# Aufruf (Mac/Linux/Git-Bash):  bash scripts/start_demo.sh
set -euo pipefail
cd "$(dirname "$0")/.."

PY="python"
command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1 && PY="python3"

echo "1/3 Backend startet auf http://localhost:8000 ..."
"$PY" -m uvicorn main:app --app-dir src/backend --port 8000 &
BACKEND_PID=$!
trap 'kill $BACKEND_PID 2>/dev/null || true' EXIT

echo "2/3 Frontend wird gebaut ..."
cd src/frontend
npm ci
NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:8000}" npm run build

echo "3/3 Frontend startet auf http://localhost:3000 (Strg+C beendet beides)"
npx next start -p 3000
