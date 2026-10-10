# Jury-FAQ: 20 wahrscheinliche Fragen mit Antwort-Gerüst

> **Jede Person muss das Produkt in 2 Sätzen erklären können:** [Satz 1: Was macht es für wen?] [Satz 2: Warum ist das besser als heute?]
> Neue Designentscheidung = neue Frage hier. Antworten kurz: **Antwort zuerst, dann ein Beleg.** Max. 20 Sekunden.
> Woher die Fragen kommen: Rubriken der EHL (Code-Qualität, Architektur, Challenge-Alignment, Innovation), Jury-Hintergründe der Partner ([SPONSOREN.md](../wissen/SPONSOREN.md)) und Muster früherer Gewinner ([VERGANGENE-PROJEKTE.md](../wissen/VERGANGENE-PROJEKTE.md)).

## Produkt und Nutzen

**1. Wer genau benutzt das, und wann?**
Gerüst: Rolle beim Partner + Situation + Häufigkeit. „Ein Sales Engineer bei [Kunde], jedes Mal wenn eine Anfrage kommt, ca. N pro Woche.“

**2. Was ist die eine Zahl, und wie habt ihr sie gemessen?**
Gerüst: „X auf N Testfällen, gelabelt von [wem], gegen Baseline Y.“ Grenze direkt mitsagen.

**3. Was ist die Baseline? Wie macht man das heute?**
Gerüst: manueller Prozess + Zeit/Kosten; oder „LLM allein ohne unsere Logik: Z %“.

**4. Warum würde [Partner] das einsetzen?**
Gerüst: Bezug auf deren Produkt/Kunden. Atira: Anfrage→Angebot schneller; tacto: Einkaufsersparnis; BMW: Kriterien aus dem Brief.

**5. Was ist an eurer Lösung neu?**
Gerüst: die eine Designidee (z. B. „LLM liest, Code entscheidet, jede Aussage mit Beleg“), nicht die Technologie.

## Technik

**6. Wie funktioniert es technisch, in einem Satz?**
Gerüst: Datenfluss aus [ARCHITEKTUR.md](../ARCHITEKTUR.md), Schritte 1-5.

**7. Was macht die KI, was macht normaler Code?**
Gerüst: „Das Modell extrahiert X als JSON (Structured Outputs). Prüfen und Rechnen macht Python, weil Modelle sich verrechnen und wir reproduzierbar sein wollen.“

**8. Welches Modell, und warum dieses?**
Gerüst: Modell + Grund (Kosten/Qualität) + was wir verglichen haben.

**9. Was passiert, wenn das Modell halluziniert?**
Gerüst: Schema-Validierung, Belegstelle muss im Original existieren, sonst „unklar“ statt erfinden.

**10. Wie skaliert das auf 1.000 Anfragen am Tag?**
Gerüst: Kosten pro Lauf × 1.000, parallele Verarbeitung, Cache; Engpass ehrlich nennen.

**11. Was kostet ein Durchlauf?**
Gerüst: Tokens × Preis, gemessen in unseren Logs. „ca. X Cent“.

**12. Wie geht ihr mit sensiblen Kundendaten um?**
Gerüst: keine Speicherung über die Sitzung hinaus, Keys nur serverseitig, für Produktion: EU-Hosting/Vertrag mit Modellanbieter.

**13. Was war die schwierigste technische Entscheidung?**
Gerüst: aus der Entscheidungstabelle in ARCHITEKTUR.md. „Wir haben X genommen, Y verworfen, weil …“

## Evaluation und Ehrlichkeit

**14. Wie wisst ihr, dass es nicht nur auf euren Beispielen funktioniert?**
Gerüst: Testset getrennt von Entwicklungsbeispielen; N Fälle; wo es scheitert (konkretes Beispiel).

**15. Was funktioniert noch nicht?**
Gerüst: 2 ehrliche Grenzen + wie man sie lösen würde. Nie „alles läuft“.

**16. Was würdet ihr mit 2 weiteren Wochen machen?**
Gerüst: 1. echtes Kundenfeedback, 2. die größte Grenze lösen, 3. Integration (CRM/ERP/Karte …).

## Team und Prozess

**17. Wie habt ihr als Team gearbeitet?**
Gerüst: 5 Rollen, jede Person mit eigenem Claude-Code-Agenten, Entire zeichnet alle Sessions auf, nur Piyush merged.

**18. Wie viel hat die KI geschrieben, und versteht ihr den Code?**
Gerüst: „Viel. Aber jede Entscheidung haben wir getroffen und begründet (sichtbar in den Entire-Checkpoints).“ Dann ein Detail aus dem eigenen Bereich erklären. Werkzeug: `entire why <datei>:<zeile>`.

**19. Was habt ihr verworfen?**
Gerüst: eine verworfene Idee + Grund (aus `docs/research/CHALLENGE.md`).

## Abschluss

**20. Warum solltet ihr gewinnen?**
Gerüst: Zahl + Alignment mit den Kriterien des Briefs + läuft live. „Wir lösen [Kriterium 1-3] nachweisbar: [Zahl].“
