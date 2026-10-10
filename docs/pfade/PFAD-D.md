# Pfad D · Lasse · PM-Cockpit (Frontend) + Design + Backup-Video

**Ziel:** Die Oberfläche, in der ein BMW-Produktmanager in 5 Minuten versteht, **was** die KI vorschlägt, **warum** und **wie sicher**, und dann entscheidet.
**Die Jury sieht vor allem das.** Darum ist dein Pfad der sichtbarste.
**Du schreibst nur in:** `src/frontend/` (Next.js, TypeScript, Tailwind).
**Du baust gegen:** das laufende Backend. Es startet auch ohne echte Daten mit dem Beispiel-Bundle:
`uvicorn main:app --app-dir src/backend --reload --port 8000` → Doku unter `http://localhost:8000/docs`, Typen aus `http://localhost:8000/openapi.json`, Vertrag in `src/shared/API.md`.
**Sprache der UI: Englisch** (siehe [`ROADMAP.md`](../ROADMAP.md) §6). Ablauf jedes Tickets: ROADMAP §4.

## Design-Regeln (in jeden Prompt, bei dem es um Aussehen geht)

- Ruhig und seriös: Navy (`#0b1f3a`) + Weiß + Grautöne, **eine** Akzentfarbe (Blau) für Aktionen. Viel Weißraum. Kein BMW-Logo.
- **Evidenz vs. Annahme immer optisch trennen:** Belege = durchgezogener Rand; Annahmen = gestrichelter Rand + Label „Assumption“.
- Evidenzstufe als Badge mit Klartext: `A · strong` grün, `B · medium` blau, `C · weak` gelb, `D · assumption` grau, Tooltip mit Begründungssatz.
- Konflikt = gelbes Badge „Conflicting evidence“ mit Link zum Gegenbefund.
- Jede Zahl mit Herkunft („38 of 3,610 comments“), kein Fachchinesisch.
- Keine Keys im Frontend; nur `NEXT_PUBLIC_API_URL` (in `src/frontend/.env.local`, nicht committen).

## Tickets

### [ ] D0 · Setup + Gerüst (30 min, ab 15:15)
**Prompt:**
> Ich bin Lasse, Pfad D, Ticket D0. Wir nehmen Next.js mit TypeScript und Tailwind, weil Claude das sehr gut kann und Seiten einzelne Dateien sind.
> Verworfen: UI-Bibliotheken wie MUI, weil jede Abhängigkeit auf 4 Laptops Setup-Risiko ist (Piyush hat nur `next`, `react`, `tailwind` freigegeben).
> Lösche `src/frontend/.gitkeep` und lege das Projekt an mit
> `npx create-next-app@latest src/frontend --typescript --eslint --tailwind --app --src-dir --import-alias "@/*" --use-npm --yes`.
> Lege `src/frontend/.env.local` mit `NEXT_PUBLIC_API_URL=http://localhost:8000` an (prüfe, dass sie gitignored ist). Prüfe `npm run lint && npm run build`.
- **Fertig, wenn:** `npm run dev` zeigt die Startseite auf `http://localhost:3000` · Build grün · `sync` (mit `package.json` und `package-lock.json`).

### [ ] D1 · API-Schicht (30 min, bis 16:15)
**Prompt:**
> Ticket D1. Baue `src/frontend/src/lib/api.ts`: TypeScript-Typen für Scenario, Signal, Evidence, Requirement (mit score_breakdown, offer_check), AuditEvent nach `src/shared/API.md`
> und `http://localhost:8000/openapi.json`, plus eine fetch-Funktion pro Endpunkt (scenarios, funnel, signals, requirements, requirement detail, decision, weights, audit, verify, export-URL).
> Basis-URL aus `NEXT_PUBLIC_API_URL`. Fehler als lesbare Meldung werfen. Warum eine Datei: Alle Seiten nutzen dieselben Typen, und bei Vertragsänderungen ändern wir nur hier.
- **Fertig, wenn:** eine Testseite listet die Anforderungen des Beispiel-Bundles · Build grün · `sync`.

### [ ] D2 · Seite 1: Anforderungsliste `/` (60 min, bis 17:15)
**Prompt:**
> Ticket D2. Startseite `/`: oben Szenario-Auswahl (Dropdown aus `GET /api/scenarios`, Standard G60-US). Tabelle nach Rang: Rang, Titel, Score als horizontaler Balken mit Zahl,
> Evidenzstufe-Badge, Kategorie, Status-Badge (proposed/challenged/approved/rejected), Konflikt-Badge falls ein verknüpfter Befund `conflicts_with` hat. Zeile klickbar → `/requirements/[id]`.
> Oben rechts Button „Export CSV“ (Link auf den Export-Endpunkt). Design-Regeln aus `docs/pfade/PFAD-D.md`. Ladezustand und Fehlermeldung, falls das Backend aus ist („Backend not reachable – start uvicorn“).
- **Fertig, wenn:** Liste zeigt Beispieldaten, Szenario-Wechsel lädt neu, Build grün, `sync`.

### [ ] D3 · Seite 2: Detail `/requirements/[id]` (75 min, bis 18:30, **M2 Durchstich**)
**Prompt:**
> Ticket D3. Detailseite aus `GET /api/requirements/{id}`. Abschnitte: Titel + Status + Evidenzstufe mit Begründungssatz; Beschreibung; **Acceptance criterion** hervorgehoben;
> **Score-Wasserfall**: pro Faktor Balken (Beitrag = value × weight × 100) mit Erklärsatz, darunter Konfidenz-Abzug durch die Evidenzstufe und Endscore;
> zwei Spalten **„Evidence“** (durchgezogen) und **„Assumptions & uncertainties“** (gestrichelt); Befunde als aufklappbare Karten → darin Belege:
> Zitat im Original, Quelle (Feedback A-D / Study / Web mit Link + Vertrauensstufe); Kasten „Already offered?“ aus `offer_check`. Zurück-Link zur Liste.
- **Fertig, wenn:** Klick Liste → Detail funktioniert mit **echten** Daten nach dem Durchstich · Build grün · `sync` · 18:30 alle zeigen lassen.
- **Subagent:** einer baut die Wasserfall-Komponente (`src/components/ScoreWaterfall.tsx`), du baust die Seite.

### [ ] D4 · Entscheiden + Prüfpfad (90 min, 19:30-21:00)
**Prompt:**
> Ticket D4. (1) Auf der Detailseite ein Entscheidungs-Panel: Buttons Approve / Reject / Edit / Challenge. **Begründung ist Pflichtfeld** (Button inaktiv ohne Text).
> Edit: Titel, Beschreibung, Kriterium, Aufwand bearbeiten. Challenge: 3 Vorschlagsfragen als Buttons („Is this only a US issue?“, „Is this just a habit of older customers?“, „What speaks against it?“) plus freies Feld;
> die KI-Antwort anzeigen mit klickbaren Beleg-IDs, Gegenbelege getrennt. Nach jeder Aktion Status und Verlauf neu laden.
> (2) Seite `/audit`: Zeitstrahl aller Ereignisse (wer: KI/Mensch/System mit Icon, was, wann, Begründung, Vorher/Nachher aufklappbar), oben Badge „Chain valid ✓“ aus `GET /api/audit/verify` (rot, wenn ungültig).
> Auf der Detailseite der Verlauf nur dieser Anforderung. Akteur-Name im UI: „pm.demo“.
- **Fertig, wenn:** Approve mit Begründung → Status grün + Eintrag in `/audit` · Challenge zeigt KI-Antwort · `sync`.
- **Subagent:** einer baut `/audit` (eigene Datei), du baust das Panel. `api.ts` änderst nur du.

### [ ] D5 · Gewichte-Regler (45 min, 21:00-21:45, **M3 um 22:00**)
**Prompt:**
> Ticket D5. Seitenleiste auf `/`: 6 Regler für die Gewichte (Namen lesbar: Customer pain, Reach, Satisfaction gap, Competitive pressure, Future relevance, Low effort) + Pflicht-Begründung + „Apply“.
> `PUT /api/scenarios/{id}/weights`, danach Liste neu; **Pfeile ↑↓ zeigen Rangänderung** gegenüber vorher (2 Sekunden hervorheben). Button „Reset to default“.
- **Fertig, wenn:** Regler „Future relevance“ hoch → Reihenfolge ändert sich, Eintrag `WEIGHTS_CHANGED` im Prüfpfad · `sync` **vor 22:00**.

### [ ] D6 · Trichter-Seite `/overview` (60 min, 22:00-23:00)
**Prompt:**
> Ticket D6. Seite `/overview` (auch als Startpunkt der Demo, Link in der Navigation): großer Trichter aus `GET /api/scenarios/{id}/funnel`:
> „3,610 customer voices → N findings → M requirements → K approved“. Darunter der Workflow in 7 Stufen (Ingest, Findings, Web, Requirements, Prioritization, Decision, Documentation)
> mit Symbolen „AI autonomous“ / „Human required“ (Inhalt: `docs/PLAN.md` §4). Ruhige Animation beim Laden (CSS, keine Bibliothek).
- **Fertig, wenn:** Seite sieht auf dem Beamer gut aus (Browserfenster 1280×720 testen) · `sync`. **Dann schlafen (Schicht 1, 23:30-03:30).**

### [ ] D7 · Politur-Runde (90 min, ab 03:30)
- Prompt: „Ticket D7. Nutze den Skill `polish` und dann `audit` auf `src/frontend`. Ziel: Demo-Strecke ohne Ruckler auf 1280×720, Ladezustände, leere Zustände, Tastatur-Fokus, keine Konsolenfehler. Nur Darstellung ändern, keine API-Änderungen.“
- Dazu Schalter „Ignore assumptions“ auf der Detailseite: Score ohne `future_relevance` aus `score_breakdown` berechnen (Formel von Dennis, C10), beide Werte nebeneinander.

### [ ] D8 · Demo-Strecke 3× (45 min, bis 06:30)
- Backend mit `DEMO_MODUS=true` starten (Piyush hat den Cache gefüllt). Drehbuch aus [`ROADMAP.md`](../ROADMAP.md) §7 dreimal durchklicken, Stoppuhr.
- Jeden Ruckler als Ticket an dich selbst; Konsolenfehler (F12) = Bug.
- **Fertig, wenn:** 3 Durchläufe ohne Fehler, jeder unter 2:30.

### [ ] D9 · Backup-Video (So 08:15-09:00, nach dem Freeze)
- Demo-Strecke als Bildschirmaufnahme (Windows: `Win+Alt+R`, Mac: `Cmd+Shift+5`), 1280×720, max. 2:30, ohne Ton (Piyush spricht live drüber, falls nötig).
- Datei **nicht ins Git** (zu groß). Auf USB-Stick + Piyushs Laptop. Ein Screenshot der Detailseite für das Deck an Piyush.

### [ ] D10 · Pitch-Teil (So 09:30-10:30)
- Du klickst live, Piyush spricht. 2× mit Stoppuhr proben. Wenn das Backend hängt: sofort Video starten, nicht debuggen.
