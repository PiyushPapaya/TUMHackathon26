# Pitch-Recherche: was ein Sieger-Pitch in 3 Minuten braucht

> Stand: So 11.10.2026, 04:30. Rahmen laut Team: **3:00 Vortrag inklusive Live-Demo + 3:00 Fragen.**
> Der alte Plan in `PITCH.md` war 4:00 + 2:00 und ist damit zu lang.
> Ergebnis dieser Recherche: der neue Ablauf in [PITCH.md](PITCH.md).

## 1. Was die Jury sieht und wer entscheidet

- **Menschen ranken**, der KI-Report ist nur Lesehilfe ([EHL-BEWERTUNG.md](../wissen/EHL-BEWERTUNG.md) Punkt 1-3).
- Die Jury sieht das **hochgeladene Deck eingebettet**, auch ohne uns. Darum braucht es zwei Teile:
  4 Vortragsfolien + einen Anhang, der **ohne Sprecher** verständlich ist.
- BMW wertet nach dem Brief (wörtlich, muss hörbar vorkommen): *trustworthy sources, transparent reasoning,
  thoughtful prioritization, uncertainty and conflicting evidence*, PM *firmly in control*, *scale across vehicle lines, markets*.

## 2. Was frühere EHL-Gewinner im Deck gemacht haben

| Team | Was wir übernehmen |
|---|---|
| TakeTheMoneyAndRun (Paris, Platz 1), `presentation/pitch_general.pdf`, 11 Folien | Problem in Alltagssprache; „warum ist das schwer“ mit einem Bild; die Idee als Vergleich aus dem Alltag; **eine Zahl gegen Alternativen** in einer Tabelle; Grenzen offen. Zwei Decks (allgemein + technisch) + Spickzettel für Fragen. |
| No Idea (Zürich, Platz 5, BMW Motorrad), `flowstate/docs/18_PITCH_AUDIT.md` | Vor dem Pitch **jede Aussage gegen den laufenden Code geprüft**; alles, was die Demo nicht zeigt, gestrichen. Folie „Was wir getestet haben und was nicht geklappt hat“ als glaubwürdigste Folie. |
| Codacabana, makalu (München 2, Platz 1) | Demo, die nie ausfällt (Safe-Demo-Modus); deterministische Logik entscheidet, das LLM liest. |

Quelle: Repos unter `github.com/european-hackathon-league`. Die BMW-Folie `decks/bmw_short.pdf` im Zürich-Repo ist das Sponsor-Deck, nicht das Team-Deck.

## 3. Allgemeine Regeln für 3-Minuten-Pitches (Web)

1. **Aufhänger in 20 s** mit einer konkreten Person oder einem Zitat und einer Zahl.
2. **Lösung in einem Satz**, dann sofort zeigen.
3. **Demo ≈ die Hälfte der Zeit (1:30-1:50)**, ein Kernablauf, stabil. Lieber 3 Momente sicher als 7 wackelig.
4. **Eine Person spricht, eine andere klickt.** Kein Code-Editor, kein Terminal.
5. **Zeit nie überziehen.** Skript auf ~390 Wörter (130 Wörter/Minute), 5× mit Stoppuhr üben.
6. **Backup-Video** bereit, langsame KI-Aufrufe vorher cachen (`DEMO_MODUS=true`).
7. Schwächen nicht im Vortrag ausbreiten, aber **ehrlich in der Fragerunde** und eine Grenze im Deck.
8. Eine Marktzahl + eine Ergebniszahl tragen den Pitch (YC-Demo-Day-Muster).

Quellen: [Reskilll](https://reskilll.com/blogs/hackathon-demo-presentation-tips-pitch-3-minutes-win-2026/) ·
[daily.dev Judging Table](https://daily.dev/posts/how-to-win-a-hackathon-notes-from-the-judging-table-wttxezbgq) ·
[Salesforce](https://developer.salesforce.com/blogs/developer-relations/2014/07/deliver-winning-pitch-hackathons) ·
[Music Hackspace](https://musichackspace.org/blog/hackathon-presentation-tips) ·
[AngelHack](https://angelhack.com/blog/10-tips-to-help-you-rock-your-next-hackathon-demo/) ·
[Xero](https://devblog.xero.com/land-your-hackathon-pitch-a-playbook-for-winning-the-room-8b327de726ca) ·
[YC Demo Day Guide](https://www.ycombinator.com/blog/guide-to-demo-day-pitches/) ·
[LTSE](https://ltse.com/insights/demo-day-tips-from-past-yc-founders)

## 4. Unsere Zahlen (nur aus Code/Daten, Stand 11.10. 04:30)

| Zahl | Wert | Quelle |
|---|---|---|
| Trichter G60-US | **3.811 Belege → 55 Befunde → 19 Anforderungen** | `data/processed/G60-US.json` → `funnel` |
| Evidenzstufen | A 3 · B 14 · C 1 · D 1 | dieselbe Datei |
| Grounding Befunde | 100 % der zitierten Beleg-IDs existieren, 100 % wörtlich in der Excel | `tests/eval/REPORT.md` |
| Grounding Anforderungen | 100 % der zitierten Befund-IDs existieren (inkl. Web-Befunde) | `tests/eval/REPORT.md` (So 06:45) |
| Messbare Kriterien | 100 % der 19 Akzeptanzkriterien enthalten eine Zahl | dieselbe Datei |
| Befund-Treue | 88 % (44 von 50 Paaren "Kommentar belegt Befund"), **von Claude gelabelt, nicht von einem Menschen**: nur Richtwert | `tests/eval/REPORT.md` (So 11.10.) |

Eval neu gelaufen (So 06:45). Vorher standen dort 89,8 % Grounding: Messfehler, weil das Skript die 5 zitierten
Web-Befunde nicht kannte. Behoben in `tests/eval/run_eval.py`. **Befund-Treue G60-US: 88 %** (44 von 50 Paaren
„Kommentar belegt den Befund“; So 08:30). Ehrlich zur Methode: Claude schlug j/n vor, Aditya prüfte und bestätigte;
die 6 „n“ sind meist Kundenfragen, die als Beschwerde zählten (z. B. „Wofür ist der Valet-Modus?“). Ein zweiter,
reiner KI-Durchlauf (Lasse) kam ebenfalls auf 88 % (Nein-Fälle dort: falsches Thema, z. B. Bluetooth unter WiFi).
Im Pitch nur mit dem Hinweis „KI-Vorschlag, von uns geprüft“ nennen.

**Konflikt-Moment der Demo (live geprüft, G60-US):** Rang 5 „Make real-world range, charging speed and charger
availability …“. Diese Anforderung zitiert **beide Seiten**: 38 Nennungen „Range feels limited and fluctuates“ gegen
28 Nennungen „Range is better than quoted and fits commute“. Fast gleich groß, also ein echter Widerspruch, kein
Ausreißer. Satz für die Demo: „Wir mitteln das nicht weg. 38 sagen zu wenig, 28 sagen mehr als versprochen. Der PM sieht
beides und entscheidet.“ Ersatz: Rang 7 Touchscreen (35 „Love the large touchscreen“ gegen 24 „Too many menus“).
Verworfen: Rang 14 Antrieb (268 gegen 32), weil das eher eine Minderheit ist als ein Widerspruch.

Dabei gefunden und behoben: Die Cockpit-Liste zeigte das gelbe „!“ auch, wenn die Gegenseite nicht zitiert war
(z. B. Rang 11 „Access systems“ gegen „Interior feels luxurious“), die Detailseite dann aber keinen Konflikt.
Jetzt gilt in Liste und Detail dieselbe Regel (`src/frontend/src/lib/conflicts.ts`).

## 5. Was daraus folgt (Entscheidungen)

- **Demo von 7 auf 3 Momente gekürzt**: Warum (Wasserfall + Zitat) · Hinterfragen + Freigeben · Gewichte ändern + Prüfpfad.
  Verworfen: Szenario-Umschalten und CSV-Export im Vortrag, weil sie 30 s kosten und keinen neuen Brief-Punkt zeigen. Beides wandert in die Fragerunde.
- **3 Minuten Fragen sind lang** → 6-8 Reservefolien (Workflow KI vs. Mensch, Formel, Architektur, F70-EU, Grenzen, Prüfpfad) und klare Zuständigkeit pro Person.
- **Nur sagen, was die Demo zeigt** (Lehre aus dem Zürich-Audit). Keine Zeitersparnis beziffern, die wir nicht gemessen haben.
