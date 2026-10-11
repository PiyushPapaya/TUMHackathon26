# Startet Backend (Port 8000) und Frontend (Port 3000) gleichzeitig, je in einem eigenen Fenster.
# Warum: Das Cockpit zeigt "Backend not reachable", sobald nur das Frontend läuft.
# Warum feste Ports: Das Frontend erwartet das Backend auf 8000; Next.js würde bei belegtem 3000 still auf 3001 ausweichen.
# Aufruf (Windows):  powershell -ExecutionPolicy Bypass -File scripts\start_dev.ps1
$root = Split-Path -Parent $PSScriptRoot

# Alte Server auf 3000/8000 beenden, damit die Ports sicher frei sind.
foreach ($port in 3000, 8000) {
    $owners = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($procId in $owners) {
        Write-Host "Port $port belegt (Prozess $procId), wird beendet ..."
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    }
}

# Demo-Modus: Antworten kommen aus dem Cache, kein OpenAI-Key nötig.
$backend = "`$env:DEMO_MODUS='true'; python -m uvicorn main:app --app-dir src/backend --port 8000"
Start-Process powershell -WorkingDirectory $root -ArgumentList '-NoExit', '-Command', $backend

# npm.cmd statt npm: Windows blockiert sonst oft npm.ps1 (Execution Policy).
$frontend = "npm.cmd run dev -- -p 3000"
Start-Process powershell -WorkingDirectory (Join-Path $root 'src\frontend') -ArgumentList '-NoExit', '-ExecutionPolicy', 'Bypass', '-Command', $frontend

Write-Host "Backend:  http://localhost:8000/docs"
Write-Host "Frontend: http://localhost:3000   (Fenster schliessen beendet den Server)"
