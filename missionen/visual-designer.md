# Mission: Visual-Designer

**Ziel:** Du baust die Bilder, die der Pitch und die App brauchen: Workflow-Diagramm, Mockups, Charts und das Bild "vom Kundenzitat zum Requirement".
**Warum für die Demo:** Pflicht-Deliverable Nr. 3 ist ein Workflow-Diagramm (KI allein vs. Mensch). Und die Jury merkt sich Bilder, nicht Absätze.

## Das entscheidest du selbst

- Der Stil (Karte E03). Du darfst vom Vorschlag abweichen, wenn du es begründest.
- Welche Zahlen auf die Charts kommen. Ein Chart mit einer Aussage schlägt drei Charts ohne.
- Wie das Bild "Zitat → Anforderung" aussieht.

## Startpunkt

Alles liegt schon in `visuals/` (siehe `visuals/README.md`): Techflow, vier Charts, drei Mockups, ein Zitat-Bild. Du machst es besser.

## Schritt für Schritt

1. Öffne `visuals/README.md` und schau jedes Bild an. Notiere pro Bild: *Was versteht man auf den ersten Blick?*
2. Wähle drei Bilder, die in den Pitch kommen. Das Techflow-Bild ist Pflicht.
3. Baue sie in Canva oder Figma nach (oder ändere die Skripte, siehe unten). Farben: ruhig, BMW-Blau (#1C69D4) als Akzent. **Kein BMW-Logo.**
4. Exportiere als PNG (Folien) und, wenn möglich, SVG. Lege sie in `visuals/` ab.
5. Trag jedes neue Bild in `visuals/README.md` ein: was es zeigt, wo es genutzt wird.
6. Sprich mit Lasse über die App-Mockups: Was davon soll wirklich in die Oberfläche?

## Charts neu bauen (mit Claude Code)

> Ändere in `scripts/make_visuals.py` den Chart 01: Zeige nur die Top 8 Themen, und färbe das größte in BMW-Blau, die anderen grau. Warum: Auf der Folie soll eine Aussage sichtbar sein. Starte danach `python scripts/make_visuals.py` und zeig mir das Bild.

## Werkzeuge

Canva oder Figma · Mermaid ([mermaid.live](https://mermaid.live)) für Diagramme als Text · Claude Code für die Charts · PowerPoint oder Google Slides.

## Fertig, wenn …

- [ ] Workflow-Diagramm (KI allein vs. Mensch) als PNG, lesbar auf einem Beamer aus fünf Metern
- [ ] Mindestens zwei Charts mit klarer Aussage in der Überschrift
- [ ] Bild "Zitat → Anforderung" für den Pitch
- [ ] Alle Bilder in `visuals/README.md` eingetragen

## Ablage und Weg in die App

PNG/SVG in `visuals/`. Folien-Bilder gehen ins Deck. Mockups gehen an Lasse (`src/frontend/`), der sie in Seiten umsetzt.
