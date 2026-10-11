# Notizen Lasse

## Gute Prompts (zum Wiederverwenden)

<!-- Ownership-Sprache: Was + Warum + Was verworfen + Wie prüfen -->

## Notizen

## Dokumentation: Mein Code (Pfad D – PM-Cockpit Frontend)

*Stand: 11.10.2026, Branch `jolesCrazyFrontend`. Geschrieben von Claude auf Bitte von Lasse, als Nachschlagewerk für mich selbst und das Team.*

### 1. Meine Rolle

Ich (Pfad D) baue die Oberfläche, mit der ein BMW-Produktmanager in 5 Minuten versteht:
**was** die KI vorschlägt, **warum**, und **wie sicher** die Belege sind – und dann entscheidet (Approve/Reject/Edit/Challenge).
Mein Bereich laut `docs/pfade/PFAD-D.md`: ausschließlich `src/frontend/` (Next.js + TypeScript + Tailwind). Backend, `src/shared/` und `core/` sind fremder Grund – ich lese dort nur.

### 2. Wo mein Code liegt

```
src/frontend/
  app/
    page.tsx                    Startseite "/" – Anforderungsliste + Gewichte-Regler
    layout.tsx                  Grundgerüst (Fonts, Dark-Mode-Script, ShaderBackground)
    globals.css                 Farben/Theme-Variablen, Dark/Light, Animationen
    audit/page.tsx              Route "/audit" -> rendert AuditPageClient
    overview/page.tsx           Route "/overview" -> rendert OverviewPageClient
    requirements/[id]/page.tsx  Route "/requirements/{id}" -> rendert RequirementDetailPageClient
  src/
    lib/api.ts                  Alle Typen + Fetch-Funktionen gegen das Backend (eine Datei für alles)
    components/
      badges.tsx                EvidenceBadge, StatusBadge, ConflictBadge, SourceTrustBadge, categoryLabel
      ScoreBar.tsx               Balken + Score-Zahl für die Listenansicht
      ScoreWaterfall.tsx         Score-Wasserfall auf der Detailseite (Faktor-Beiträge + Konfidenz-Abzug)
      FindingCard.tsx            Aufklappbare Befund-Karte mit Original-Zitaten
      DetailBlocks.tsx           AssumptionItem (gestrichelte Box), OfferCheckBox ("Already offered?")
      DecisionPanel.tsx          Approve/Reject/Edit/Challenge inkl. Pflicht-Begründung + KI-Antwort
      AuditTrail.tsx             Zeitstrahl aller Ereignisse (für /audit und für die Detailseite)
      RequirementDetailView.tsx  Baut die Detailseite aus allen Bausteinen zusammen
      RequirementDetailPageClient.tsx  Lädt die Daten für die Detailseite, hält State
      OverviewPageClient.tsx     Trichter-Seite ("3.610 Stimmen -> ... -> genehmigt") + 7-Stufen-Workflow
      AuditPageClient.tsx        Seiten-Rahmen um AuditTrail für die eigenständige "/audit"-Seite
      ThemeToggle.tsx            Hell/Dunkel-Umschalter oben rechts
      ShaderBackground.tsx       Animierter WebGL-Hintergrund (ruhiger Verlauf, kein Framework)
```

### 3. Wie die Daten fließen

1. **`src/lib/api.ts`** ist die einzige Stelle, die das Backend kennt. Sie definiert TypeScript-Typen (`Requirement`, `Signal`, `Evidence`, `AuditEvent`, ...) passend zu `src/shared/API.md`, plus eine Funktion pro Endpunkt (`getScenarios`, `getRequirements`, `getRequirementExplain`, `postDecision`, `putWeights`, `getAudit`, `getExportUrl`, ...).
   Warum eine Datei: Wenn sich der Vertrag zum Backend ändert, ändere ich nur hier etwas – alle Seiten nutzen dieselben Typen.
   Eine zentrale `request()`-Funktion fängt Netzwerkfehler ab und wirft die lesbare Meldung „Backend not reachable – start uvicorn", statt dass die Seite crasht.
2. Jede Seite (`page.tsx`, `OverviewPageClient.tsx`, `RequirementDetailPageClient.tsx`, `AuditPageClient.tsx`) lädt ihre Daten per `useEffect` + den Funktionen aus `api.ts` und hält sie in React-State (`useState`). Ladezustand und Fehlermeldung sind überall gleich behandelt.
3. Komponenten wie `ScoreWaterfall`, `FindingCard`, `badges.tsx` bekommen nur fertige Daten als Props – sie rufen selbst nie das Backend. Das hält die Datenflüsse an einer Stelle nachvollziehbar.

### 4. Die vier Seiten im Detail

**`/` – Anforderungsliste (`app/page.tsx`, 306 Zeilen)**
Kopfzeile mit Szenario-Dropdown (`GET /api/scenarios`, Standard `G60-US`) und drei Kennzahlen-Kacheln (Stimmen/Findings/Requirements). Tabelle: Score-Balken, Titel+Beschreibung, Kategorie – Zeile komplett klickbar (Maus und Tastatur, `role="link"` + `onKeyDown`) zur Detailseite. Rechts eine feste Spalte mit „Demo navigation" (4-Schritte-Anleitung für die Jury-Demo) und den 6 Gewichte-Reglern (siehe D5-Ticket). Nach „Apply weights" merkt sich die Seite die alten Ränge und hebt 2 Sekunden lang die Zeilen hervor, die sich verschoben haben.

**`/requirements/[id]` – Detailseite**
`RequirementDetailPageClient.tsx` lädt `getRequirementExplain(id)` und hält den Zustand „Ignore assumptions" (Umschalter, der den Score ohne `future_relevance` neu zeigt). `RequirementDetailView.tsx` setzt daraus die Seite zusammen: Titel+Status+Evidenzbadge, Beschreibung, **Acceptance criterion** in eigenem Kasten, **Score-Wasserfall**, optional Robustheit/Business-Kontext, zweispaltig **Evidence** (durchgezogener Rand) vs. **Assumptions & uncertainties** (gestrichelter Rand), Web-Quellen, „Already offered?"-Box, Entscheidungs-Panel, und zuletzt der Prüfpfad nur für diese Anforderung.

**`/audit` – Prüfpfad**
Eigenständige Seite, zeigt denselben `AuditTrail` wie die Detailseite, aber ungefiltert (alle Ereignisse). Jedes Ereignis: wer (KI/Mensch/System-Icon-Label), was, wann, Begründung, und ein aufklappbares Vorher/Nachher-JSON.

**`/overview` – Trichter-Seite (für den Demo-Start)**
Großer Trichter „customer voices -> findings -> requirements -> approved" mit sanfter Einblend-Animation (reines CSS, `@keyframes funnel-enter`), Top-3-Vorschläge, Verteilung der Evidenzstufen, und die 7-Stufen-Workflow-Übersicht mit „AI autonomous" / „Human required"-Kennzeichnung je Pfad.

### 5. Design-System (`globals.css`)

Alle Farben sind CSS-Variablen (`--background`, `--foreground`, `--surface`, `--accent`, `--accent-hover`, `--table-background`, `--score-slider`), einmal für Hell (`:root`) und einmal für Dunkel (`.dark`). Tailwind liest sie über `@theme inline` ein. `ThemeToggle.tsx` schaltet nur die `.dark`-Klasse auf `<html>` um und merkt sich die Wahl in `localStorage`; ein kleines Inline-Script in `layout.tsx` setzt die Klasse schon vor dem ersten React-Render, damit es nicht kurz flackert.

Für Jury-Screenshots, die *immer gleich* aussehen sollen (unabhängig vom Dark-Mode-Stand des Browsers), gibt es zwei Hilfsklassen, die die Variablen lokal festnageln: `.theme-light-fixed` und `.theme-dark-fixed`. Die „Demo navigation"-Box auf `/` und die „Acceptance criterion"-Box auf der Detailseite nutzen `.theme-dark-fixed`.

`ShaderBackground.tsx` zeichnet einen ruhigen, animierten Verlauf per WebGL (Value-Noise statt teurem Simplex-Noise, läuft nur im Browser, fällt ohne WebGL einfach auf den CSS-Hintergrund zurück).

### 6. Was ich bisher committet habe (chronologisch, Kurzfassung)

Reihenfolge, "Was" + "Warum" in eigenen Worten – Volltext mit Verworfen/Geprüft steht in den Commit-Nachrichten selbst (`git log --author=Lasse`):

1. **Projekt-Grundgerüst** (`ddbf612`) – Next.js/TS/Tailwind statt UI-Bibliothek wie MUI, weil jede zusätzliche Abhängigkeit auf 4 Laptops Setup-Risiko ist.
2. **API-Schicht `api.ts`** (`da1f672`) – ein Ort für Typen und Fetch-Funktionen, damit Vertragsänderungen nur eine Datei betreffen.
3. **D2: Anforderungsliste `/`** (`0c1c4f9`) – Rang, Score, Evidenzstufe, Kategorie, Status, Konflikte auf einen Blick; Konflikt-Erkennung bewusst im Frontend verdrahtet (Signal.conflicts_with), weil das Backend das schon mitliefert und keine Vertragsänderung nötig war.
4. **D3: Detailseite** (`12d2f8f`) – aus `GET /api/requirements/{id}`.
5. **Cockpit-Layout überarbeitet** (`45fb5ec`) – Top-Bar/Tabelle/Prompt-Zeile, alte „Studio"-Reste entfernt.
6. **WebGL-Shader-Hintergrund** (`77e1377`, `4eac188`) – ruhiger animierter Verlauf, später auf dunkelblau mit Hue-Shift umgestellt.
7. **Dark Mode** (`741d571`, `8d4265b`) – Umschalter zuerst eingebaut, dann in die Top-Bar hinter „Export CSV" verschoben.
8. **Shader schneller/heller** (`21f6006`) – wirkte auf dem dunklen Theme zu statisch und zu dunkel.
9. **Oberflächen-Farbe zentralisiert** (`9f29cf1`) – Karten/Kopfzeile/Felder über `--surface`-Variable statt pro Komponente hart codiert.
10. **Tabellen-Höhe/Scroll-Fixes** (`50ee635`, `8a545f1`, `6b09827`) – erst feste Höhe mit Scrollbox ausprobiert, dann wieder verworfen, weil normales Seiten-Scrollen besser funktionierte.
11. **Hydration-Warnungen behoben** (`0a34145`, `1a79b7f`) – `suppressHydrationWarning` an Theme-Button und `<html>`, weil Server und Browser beim ersten Rendern unterschiedliche Dark-Mode-Stände haben dürfen (das ist kein Bug, sondern erwartetes Verhalten bei `localStorage`-Themes).
12. **Layout-Feinschliff** (`781bdd5`) – Listen- und Detailseite abgeschlossen.
13. **Demo-Navigation fixiertes Farbschema** (`20bfb96` → dann `4765838`) – zuerst hell fixiert, dann auf dunkel fixiert umentschieden (gefiel optisch besser); neue CSS-Klassen `.theme-light-fixed`/`.theme-dark-fixed` statt globalem Dark-Mode-Umschalten, weil das den Rest der Seite mitgeändert hätte.
14. **Rationale-Feld bei Gewichte-Reglern entfernt** (`d1779cd`) – Feld + „Use demo rationale"-Button raus, weil die Wirkung nicht nachvollziehbar war und ein unklares Feld schlechter ist als keins.
15. **Acceptance-Criterion-Box dauerhaft dunkel** (`c7abe2a`) – nutzt die schon vorhandene `.theme-dark-fixed`-Klasse (gleiches Muster wie bei der Demo-Navigation), damit es für Jury-Screenshots immer gleich aussieht.

Dazwischen gab es mehrere `Merge`-Commits, weil alle direkt auf `main` arbeiten (Backend-Stand von Dennis/Piyush eingeholt, ohne dass sich das mit meinem Frontend-Code überschnitten hat).

*Hinweis:* In der Commit-Historie unter meinem Namen stehen auch einige Backend-Tickets (z. B. „L17"–„L22", „L27", „P0.1"). Die habe ich der Vollständigkeit halber nicht ausgewertet, weil sie laut Ownership-Tabelle nicht zu Pfad D gehören (`src/backend/core/`, Pipeline, `data/README`) – das sollte Piyush/der jeweilige Pfad einordnen, falls das falsch zugeordnet wurde.

### 7. Aktueller Stand – noch nicht committet

Im Arbeitsverzeichnis liegen gerade drei **ungespeicherte** Änderungen (`git status` auf `jolesCrazyFrontend`):

- `app/globals.css`: ein Leerzeichen am Zeilenende bei `--accent-hover` – sieht nach einem versehentlichen Tastendruck aus, keine inhaltliche Änderung.
- `app/page.tsx` und `src/components/AuditPageClient.tsx`: der Navigationslink „Overview" wurde aus der Top-Bar entfernt (auf beiden Seiten identisch).

Die `/overview`-Seite selbst existiert weiterhin und verlinkt noch zurück auf „Requirements" und „Audit trail" – nur der Weg *hin* zu `/overview` über die Top-Bar fehlt jetzt auf `/` und `/audit`. Das ist nicht committet und auch noch nicht im Commit-Verlauf erklärt (kein Warum hinterlegt) – bevor das per `sync` auf `main` geht, sollte ich kurz festhalten, ob das Absicht ist (z. B. weil D6/`/overview` nur noch über einen Demo-Start-Link erreicht werden soll) oder ein Zwischenstand.

### 8. Offene Punkte aus meinem Arbeitsbuch (`docs/pfade/PFAD-D.md`)

Nur D3 ist als „fertig" markiert (`[x]`). Tatsächlich committet ist inhaltlich bereits mehr (D0–D6 laut Code vorhanden), die Checkboxen im Arbeitsbuch sind aber nicht nachgezogen. Noch offen laut Ticketliste:
- **D7 Politur-Runde** – Skill `polish`/`audit` auf `src/frontend`, Ladezustände/leere Zustände/Tastaturfokus/Konsolenfehler.
- **D8 Demo-Strecke 3×** – mit `DEMO_MODUS=true` durchklicken, Stoppuhr, jeder Ruckler als Ticket.
- **D9 Backup-Video** – Bildschirmaufnahme, nicht ins Git.
- **D10 Pitch-Teil** – Live-Klicken proben.
