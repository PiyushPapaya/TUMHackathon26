---
name: demo-check
description: Prüft, ob unser Repo bei einem Fremden läuft („would it run“): frischer Clone, README wörtlich befolgen, Hauptflow testen. Benutzen bei „läuft das?“, „demo-check“, „Fresh-Clone-Test“, vor jeder Abgabe und So ab 08:30.
---

# Demo-Check (Fresh Clone)

Der EHL-Reviewer urteilt „would it run: yes/probably/unlikely/no“ nur aus Setup-Dateien und Code. Die Jury klickt den Demo-Link. Beides prüfen wir hier wie ein Fremder.

## Schritte

1. **Temp-Ordner außerhalb des Repos** anlegen (z. B. im System-Temp oder Claude-Scratchpad).
2. **Frisch klonen, Stand `main`:** `git clone --depth 1 https://github.com/PiyushPapaya/TUMHackathon26.git demo-check && cd demo-check`.
3. **README-Quickstart wörtlich ausführen**, Befehl für Befehl, ohne Vorwissen. Nichts aus dem echten Repo kopieren. Fehlende `.env`: nur `.env.example` kopieren und `DEMO_MODUS=true` setzen (keine echten Keys in Temp-Ordner schreiben, außer die Person gibt es ausdrücklich frei).
4. **Jeden Befehl protokollieren:** Befehl → Ergebnis (ok / Fehler + erste Fehlerzeile).
5. **Hauptflow testen:**
   - Backend: `GET /health` → 200; `GET /api/scenarios/G60-US/requirements` und `POST .../decision` → erwartete Form laut `src/shared/API.md`.
   - Frontend: Seite lädt, Demo-Strecke aus `docs/pitch/PITCH.md` einmal durchklicken (oder per `curl` prüfen, wenn kein Browser).
   - Live-Demo-URL aus der README öffnen (Inkognito-Gedanke: kein Login, keine lokalen Daten).
6. **Statische Prüfung wie der Reviewer:** Sind alle Imports in `requirements.txt` / `package.json`? Gibt es offensichtliche Crash-Stellen (fehlende Env-Variable ohne Fehlermeldung, harte Pfade wie `C:\Users\…`)?
7. **Aufräumen:** Temp-Ordner löschen (nur den, den du in Schritt 1 angelegt hast).

## Ausgabe

```
Urteil: would it run = yes | probably | unlikely | no
Quickstart: N/M Befehle ok
Hauptflow: ✅/❌ (Details)
Live-URL: ✅/❌
Fixes (priorisiert):
1. <Problem> → <Änderung in Datei> → <Owner>
```

Fixes nicht selbst in fremden Ordnern machen. Liste an die Owner bzw. an Piyush (README).
