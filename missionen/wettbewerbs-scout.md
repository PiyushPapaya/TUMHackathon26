# Mission: Wettbewerbs-Scout

**Ziel:** Du recherchierst, wie Mercedes, Audi, Tesla, Genesis und Lucid unsere Top-Kundenthemen lösen, und lieferst eine Tabelle mit Link pro Quelle.
**Warum für die Demo:** Der Brief will "competitor advantages" und vertrauenswürdige Quellen. Eine Anforderung wie "physische Tasten für Lautstärke" wird stärker, wenn drei Wettbewerber es schon bieten oder gerade zurückbauen.

## Das entscheidest du selbst

- Welche 5 bis 8 Themen du recherchierst (nimm die Top-Themen aus `visuals/charts/01_...png`).
- Welche Quellen du vertraust: Testmagazin (Car and Driver, Motor Trend, auto motor und sport) zählt mehr als ein Forum.
- Ob etwas ein echter Vorteil ist oder nur Werbung.

## Schritt für Schritt

1. Wähle ein Thema, z. B. "Touch-Bedienung vs. Tasten".
2. Suche für jeden Wettbewerber: Was bietet er dazu im aktuellen Modell? (E-Class, A6 e-tron, Model S, Genesis G80, Lucid Air. Die Liste steht in `config/scenarios/G60-US.json`.)
3. Pro Fund eine Tabellenzeile mit **Link** und **Datum**. Ohne Link zählt es nicht.
4. Bewerte die Quelle: `high` (etabliertes Magazin, Hersteller), `medium` (Fachblog), `low` (Forum, Reddit).
5. Schreib dazu: **stützt** die Quelle die Anforderung, oder **widerspricht** sie? Widersprüche sind wertvoll.
6. Gib Piyush die Tabelle. Er vergleicht sie mit dem, was die KI-Websuche gefunden hat (Pfad B).

## Tabelle

| Thema | Wettbewerber | Was sie bieten | Link | Datum | Vertrauen | stützt / widerspricht |
|---|---|---|---|---|---|---|
| Bedienung | | | https://... | | high | stützt |

## Werkzeuge

Browser · Claude oder ChatGPT mit Websuche ("Finde Quellen zu X, mit Link und Datum") · Excel oder Google Sheets. **Prüfe jeden Link selbst.** KI erfindet manchmal URLs.

## Fertig, wenn …

- [ ] Mindestens 5 Themen mit je 2 bis 3 Quellen (also 10 bis 15 Zeilen)
- [ ] Jede Zeile hat einen Link, den du selbst geöffnet hast
- [ ] Mindestens ein Widerspruch dabei
- [ ] Zwei Zeilen in `notizen.md`: welche Quelle du aussortiert hast und warum

## Ablage und Weg in die App

`werkstatt/<name>/scout_tabelle.csv`. Piyush lädt sie als zusätzliche Webbelege in `evidence_external/` (Tickets B1 bis B5). Die Vertrauensstufe berechnet der Code aus der Domain, deine Einschätzung dient als Gegenprobe, und Abweichungen sind eine gute Jury-Geschichte.
