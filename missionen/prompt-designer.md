# Mission: Prompt-Designer

**Ziel:** Du schreibst und testest die Anweisungen (Prompts), mit denen die KI Anforderungen formuliert und auf Challenges antwortet.
**Warum für die Demo:** Die Textqualität der Anforderungen und die Challenge-Antwort sind das, was die Jury live sieht. Ein guter Prompt macht aus "Verbessere die Bedienung" ein "Lautstärke, Klima und Defrost sind in einem Handgriff ohne Menü erreichbar".

## Das entscheidest du selbst

- Wie klingt eine gute Anforderung? Länge, Ton, Messkriterium, Zahl oder Ja/Nein.
- Welche Regeln sind hart? (Keine Technik-Specs, kein Preis, nur IDs aus der Eingabe, Annahmen getrennt nennen.)
- Wie klingt die Challenge-Antwort? Verteidigt sie sich oder gibt sie nach, wenn die Gegenbelege stark sind?

## Schritt für Schritt

1. Lies den aktuellen Prompt: `src/backend/requirements_engine/derive.py` (Suche nach dem langen Text-Block) und `challenge.py`. Du musst nichts verstehen, nur den Text lesen.
2. Schreib auf, was du schlecht findest. Beispiel: "Zwei Anforderungen sagen fast dasselbe", "Kriterium nicht messbar".
3. Formuliere die Regel als Satz: "Jede Anforderung hat genau ein messbares Kriterium mit Zahl."
4. Gib Claude Code deinen Satz (Vorlage unten). Claude baut ihn in den Prompt und lässt den Test laufen.
5. Lass die Ableitung laufen und prüfe das Ergebnis mit der Checkliste unten.
6. Wiederhole mit der Challenge. Teste drei Fragen: eine berechtigte, eine unfaire, eine, bei der die Antwort "stimmt, ändern wir" sein muss.

## Vorlage für Claude Code

> Wir verbessern den Prompt in `src/backend/requirements_engine/derive.py`. Neue Regel: <deine Regel>. Warum: <was bisher schiefging>. Verworfen: <was du nicht willst>. Prüf es, indem du `python -m pytest tests/pfad_c -q` laufen lässt und zeigst mir danach zwei Beispiel-Anforderungen vorher und nachher.

(Der Ordner `src/backend/requirements_engine/` gehört Dennis. Änderungen im Prompt macht er oder du über seine Claude-Session.)

## Qualitäts-Checkliste (pro Anforderung)

- [ ] Kundensicht, keine Technik ("Wasserpumpe 12 V" ist falsch)
- [ ] Messbares Kriterium ("80 % blind bedienbar")
- [ ] Annahmen stehen getrennt, nicht im Fließtext
- [ ] Keine Doppelung zu einer anderen Anforderung
- [ ] Alle `signal_ids` existieren wirklich

## Werkzeuge

Claude Code · ChatGPT oder Claude im Browser zum Ausprobieren von Formulierungen · eine Textdatei mit Vorher/Nachher.

## Fertig, wenn …

- [ ] Drei Prompt-Änderungen mit je Was, Warum, Verworfen in `werkstatt/<name>/notizen.md`
- [ ] Vorher/Nachher von mindestens fünf Anforderungen
- [ ] Drei Challenge-Fragen mit guter Antwort für den Pitch

## Ablage und Weg in die App

Die geänderten Prompts stehen im Code (`derive.py`, `challenge.py`), die Nachweise in `werkstatt/<name>/`. Die besten Challenge-Fragen gehen in `docs/07_pitch.md` (Demo-Klickpfad, Schritt 4).
