# Pfad D · PM-Cockpit (Frontend)

**Ziel:** Die Oberfläche, in der der PM in 5 Minuten versteht, **was** die KI vorschlägt,
**warum** und **wie sicher**, und dann entscheidet. Die Jury sieht vor allem das.
**Du schreibst in:** `src/frontend/` (Next.js, TypeScript, Tailwind).
**Du baust gegen:** das laufende Backend mit Beispieldaten (`uvicorn main:app --app-dir src/backend --reload --port 8000`)
und `src/shared/API.md`. Typen kannst du aus `http://localhost:8000/openapi.json` ableiten.

## Seiten (in dieser Reihenfolge bauen)

| # | Seite | Inhalt | Endpunkte |
|---|---|---|---|
| 1 | **Anforderungsliste** `/` | Tabelle nach Rang: Titel, Score-Balken, Evidenzstufe (A grün … D grau), Kategorie, Status, Konflikt-Badge; Szenario-Auswahl oben | `GET /api/scenarios`, `GET /api/scenarios/{id}/requirements` |
| 2 | **Detail** `/requirements/[id]` | Beschreibung, Akzeptanzkriterium, **Score-Wasserfall** (Faktor × Gewicht = Beitrag + Erklärsatz), Annahmen vs. Belege getrennt, Befunde aufklappbar → Zitate/Webquellen mit Link, "Gibt es das schon?" | `GET /api/requirements/{id}` |
| 3 | **Entscheiden** (auf Detail) | Buttons Freigeben / Ablehnen / Bearbeiten / Hinterfragen; **Begründung ist Pflichtfeld**; KI-Antwort bei Challenge mit Beleg-Links | `POST /api/requirements/{id}/decision` |
| 4 | **Prüfpfad** `/audit` + Verlauf auf Detail | Zeitstrahl: wer (KI/Mensch/System), was, wann, warum, Vorher/Nachher; Badge "Kette gültig ✓" | `GET /api/audit`, `GET /api/audit/verify` |
| 5 | **Priorisierung** (Seitenleiste auf `/`) | 6 Regler für die Gewichte + Begründungsfeld → Liste rankt neu, Pfeile zeigen Rangänderung | `PUT /api/scenarios/{id}/weights` |
| 6 | **Trichter** `/overview` | "3.610 Stimmen → 30 Befunde → 12 Anforderungen → 5 freigegeben" (wie BMW-Folie "1 Billion → 1,000 → One car") + Workflow mit KI/Mensch-Symbolen | `GET /api/scenarios/{id}/funnel` |
| 7 | Export-Button | CSV der Anforderungsliste | `GET /api/scenarios/{id}/export` |

## Schritte

| # | Zeitbox | Aufgabe | Fertig, wenn … |
|---|---|---|---|
| 0 | 15 min | Gerüst: `npx create-next-app@latest src/frontend --typescript --eslint --tailwind --app --src-dir --import-alias "@/*" --use-npm` (Lead bestätigt neue Dependencies) | `npm run dev` zeigt Seite |
| 1 | 30 min | `src/lib/api.ts`: Typen + fetch-Funktionen, Basis-URL aus `NEXT_PUBLIC_API_URL` | Liste lädt echte Beispieldaten |
| 2 | 90 min | Seite 1 + 2 | **Sa 18:00**: Klick von Liste auf Detail mit Wasserfall |
| 3 | 90 min | Seite 3 + 4 | **Sa 22:00**: Entscheidung erscheint sofort im Verlauf |
| 4 | 60 min | Seite 5 + 6 | Regler ranken live um |
| 5 | Nacht | Politur: BMW-nahe, ruhige Optik (dunkles Blau, viel Weißraum), Ladezustände, Fehlermeldungen, Tastatur-Fokus | Demo-Strecke ohne Ruckler |
| 6 | So früh | Demo-Strecke 3× durchklicken mit `DEMO_MODUS=true` | keine Konsolenfehler |

## Design-Regeln

- **Evidenz vs. Annahme immer optisch trennen** (z. B. Belege = durchgezogener Rand, Annahmen = gestrichelt + Icon).
- Konflikte sichtbar machen (gelbes Badge "Widersprüchliche Belege" → Link zum Gegenbefund).
- Kein Fachchinesisch: "Evidenzstufe A: 61 Nennungen aus Feedback + Studie" statt "EL=A".
- Keine Keys im Frontend; nur `NEXT_PUBLIC_API_URL`.

## Start-Prompt für Claude

> "Ich baue Pfad D. Wir bauen das Frontend gegen das echte Backend mit Beispieldaten statt gegen
> eigene Mocks, weil das Backend schon läuft und wir so Vertragsfehler sofort sehen. Bitte baue
> `src/frontend/src/lib/api.ts` mit Typen nach `src/shared/API.md` und die Seite `/` als Tabelle
> nach Rang mit Score-Balken und Evidenz-Badge. Verworfen: UI-Bibliothek mit vielen Abhängigkeiten,
> Tailwind reicht. Prüfen mit `npm run lint && npm run build`."

## Deine Pitch-Folie + Demo-Abschnitt

- Folie: Screenshot Detailseite mit Wasserfall und Belegkette.
- Demo: Du klickst live (oder führst den Klickpfad), der Lead spricht.
