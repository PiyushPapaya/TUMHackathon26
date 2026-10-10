# 02 Glossar

Jeder Begriff in einem Satz, mit einem Beispiel aus unseren Daten. Fehlt ein Wort? Claude fragen und hier eintragen. Git-Wörter (commit, push, merge) stehen in `docs/wissen/GLOSSAR.md`.

## Unser Produkt

| Begriff | Ein Satz | Beispiel |
|---|---|---|
| **PM (Produktmanager)** | Die Person bei BMW, die entscheidet, was ins nächste Modell kommt. | Sie sieht Platz 1 der Liste und klickt "approve". |
| **Requirement / Anforderung** | Ein klarer, messbarer Satz, was das Auto aus Kundensicht können muss. | "Lautstärke und Klima sind ohne Blick auf den Bildschirm bedienbar." |
| **Finding / Befund (Signal)** | Ein wiederkehrendes Thema aus vielen Quellen: Beschwerde, unerfüllter Wunsch, Lob, Wettbewerbsvorteil oder Trend. | "Touch-only-Bedienung lenkt ab", belegt durch viele Kommentare. |
| **Evidenz / Beleg** | Ein einzelnes Stück Beweis mit fester ID: ein Kommentar, eine Studienzeile, eine Webquelle. | `G60-0019`: "Center console layout is terrible." |
| **Evidenzstufe A-D** | Regelbasierte Note, wie gut eine Anforderung belegt ist. A = Kommentare, Studie und Web stützen sie. D = fast nur Annahme. | Eine Anforderung nur mit Webtrend, ohne Kundenzitat, bekommt D. |
| **Annahme** | Etwas, das wir für die Zukunft glauben, aber nicht belegen können. | "Sprachsteuerung ersetzt bis 2030 viele Tasten." |
| **Konflikt** | Zwei Befunde widersprechen sich. Wir zeigen beides. | "Großes Display gelobt" gegen "Touch-Bedienung kritisiert". |
| **Score** | Zahl von 0 bis 100, die die Priorität ausdrückt. Eine Formel in Python, kein KI-Urteil. | Siehe `entscheidungen/E05_priorisierung.md`. |
| **Gewichte** | Wie stark jeder Faktor im Score zählt. Der PM kann sie ändern. | Kundenschmerz 25 %, Reichweite 20 %. |
| **Challenge** | Der PM hinterfragt eine Anforderung, die KI antwortet mit Belegen und Gegenbelegen. | "Ist das nur eine Gewohnheitsfrage älterer Kunden?" |
| **Audit Trail** | Protokoll jeder Änderung: wer, was, wann, warum, vorher, nachher. Jeder Eintrag ist mit dem vorherigen verkettet (Hash-Kette), heimliches Ändern fällt auf. | `PM_APPROVED` mit Begründung. |
| **Szenario** | Eine Kombination aus Modell und Markt, als JSON-Datei. | `G60-US` |
| **Optionsliste** | Die offizielle Liste aller Ausstattungen und Pakete eines Modells (PDF). | `G60_OptionList.PDF` |

## BMW-Daten

| Begriff | Ein Satz | Beispiel |
|---|---|---|
| **G60 / G70 / F70** | Interne Modellcodes: 5er Limousine, 7er, 1er. | Demo-Fall ist der G60. |
| **Source A-D** | Woher ein Kommentar kommt (vier verschiedene Quellen-Typen). | G60 US: Source B hat 2.627 Zeilen, die meisten. |
| **Feedback Type** | Art des Kommentars: Likes, Difficult to Use, Wants, Defect. | G60 US: 1.217 mal "Difficult to Use". |
| **VFC / Taxonomie** | BMWs eigene Themen-Einteilung für Kommentare, in Ebenen. | `Vfc level2 Name` = "Touch screen, operation" |
| **Kundenstudie** | Befragung mit 7 Antwortstufen von "I Hate It" bis "I Love It" je Attribut. | G60 USA: 15,0 % unzufrieden mit "Operation of heater/ AC controls". |
| **Absatzzahlen** | Verkaufte Fahrzeuge pro Markt für 2024, 2025 und Prognose 2030. | 5er USA: 75.600 / 78.000 / 80.000 |

## Technik

| Begriff | Ein Satz | Beispiel |
|---|---|---|
| **Pipeline** | Die Kette von Schritten, die Rohdaten in Anforderungen verwandelt. | `python src/backend/pipeline.py --scenario G60-US` |
| **Stufe** | Ein Schritt der Pipeline. Jede schreibt eine JSON-Datei. | `signals.json` |
| **JSON** | Textformat für strukturierte Daten. | `{"id": "SIG-G60-US-001", ...}` |
| **LLM** | Das Sprachmodell (hier von OpenAI), das Texte liest und schreibt. | Es formuliert Anforderungen aus Befunden. |
| **Prompt** | Die Anweisung an das LLM. Prompts schreiben ist echtes Bauen. | "Fasse diese Kommentare zu einem Befund zusammen und nenne die IDs." |
| **Grounding / Halluzinationsschutz** | Die KI darf nur IDs zitieren, die wir ihr gegeben haben. Ein Test prüft das. | Erfundene Kommentar-ID wird abgelehnt. |
| **Cache / Demo-Modus** | Gespeicherte KI-Antworten, damit die Demo ohne Internet läuft. | `DEMO_MODUS=true` |
| **API** | Die "Speisekarte" des Backends: welche Anfrage welche Antwort liefert. | `GET /api/scenarios/G60-US/signals` |
| **Backend / Frontend** | Backend rechnet (FastAPI), Frontend zeigt (Next.js). | `src/backend/` und `src/frontend/` |
| **Entire** | Tool, das unsere Claude-Sessions aufzeichnet. Pflicht für die Abgabe. | `entire status` |
| **Mermaid** | Text, aus dem ein Diagramm wird. GitHub zeigt es automatisch. | Alle Diagramme in diesen Docs |
