# UX und BMW-Briefing: Abgleich vom 11.10.2026

Stand: Branch `piyush-frontend`. Quellen sind die zwei lokal bereitgestellten
Briefing-PDFs, die beiden Prozessbilder und die Excel-/Optionslisten-Dateien.
Ein Discord-Export liegt nicht vor und es ist kein Discord-Zugriff verbunden.
Dieser Bericht bestaetigt deshalb keine Discord-Absprachen. Die im Auftrag
genannten UI-Bilder #22 bis #28 waren nicht angehaengt.

## Was BMW erwartet

Die beiden zweitseitigen PDFs enthalten denselben Aufgabentext. Gefordert ist
Entscheidungsunterstuetzung fuer einen Product Manager: kundenbezogene
Anforderungen fuer einen Nachfolger in drei bis fuenf Jahren, begruendet durch
Feedback, Produktdaten, Absatz, Studien und geeignete externe Recherche.
Evidenz, Annahmen, Unsicherheit und widerspruechliche Belege sollen erkennbar
bleiben. Der PM muss pruefen, hinterfragen, bearbeiten, freigeben und ablehnen
koennen. Eine bestimmte Architektur oder gleich hohe Reife aller Faehigkeiten
ist nicht vorgeschrieben (Briefing, Seite 2).

Die Prozessfolie ist ein groesseres Zielbild. Technische Detailauslegung und
vollstaendige Wirtschaftlichkeitsrechnungen sind kein notwendiges Deliverable
dieses Prototyps. Aktuelle Listenpreise sind sinnvoller Produktkontext, aber
kein Beleg fuer Entwicklungskosten, Zahlungsbereitschaft oder einen 2030-Preis.

## Datenabdeckung

| Eingabe | Lokal geprueft | Verwendung / Grenze |
|---|---|---|
| F70-Feedback | 4.076 Datenzeilen, 12 Spalten | Land, Antrieb, Quelle, Originalkommentar und BMW-Taxonomie vorhanden |
| G60-Feedback | 5.005 Datenzeilen, 12 Spalten | Gleicher Aufbau; nicht alle Zeilen gehoeren zum US-Markt |
| G70-Feedback | 4.690 Datenzeilen, 12 Spalten | Gleicher Aufbau; Likes und Dislikes nicht wegmitteln |
| Kundenstudien | CN_EU_2025 und US_2025 | Unterschiedliche Skalen; fehlende Zuordnung zum Befund sichtbar lassen |
| Absatz | F70, G60_G68, G70; 2024/2025/2030 | Marktvolumen ist Kontext, keine direkte Kundenstimme; 2030 ist eine Projektion |
| Optionslisten | F70: 23, G60: 28, G70: 27 Seiten | DE-Angebot; nicht ungeprueft als US-/CN-Verfuegbarkeit ausgeben |
| G68 | Kein separates Feedback und keine eigene Optionsliste geliefert | Kaltstart / begrenzte Abdeckung deutlich machen |
| Externe Quellen | Web-/Statistik-Endpunkte und Quellenfelder vorhanden | Aktualitaet und inhaltliche Qualitaet nicht allein durch vorhandene URL bewiesen |

Die Zahlen oben beschreiben die Eingabedateien, nicht die Zahl der Belege in
einem Szenario. Szenariozahlen im Pitch aus dem laufenden Backend ablesen.
Die zwei Prozessbilder sind Konzeptfolien, kein gemessener Datensatz mit
einer Milliarde verarbeiteter Befunde.

## Umsetzung in dieser Ueberarbeitung

| Bedienproblem | Umsetzung |
|---|---|
| Modelle/Regionen schwer auffindbar | Eigene Seite `/models`, Navigation, Suchfeld und Modell-/Regionsfilter; auch in der Startseiten-Auswahl |
| Rangliste ohne gezielte Auswahl | Suche, Thema, Status, Evidenz, Aufwand, Konfliktfilter und Sortierung |
| Score erst nach Scrollen | Detailkopf mit Anforderung und Beitragschart nebeneinander |
| Unklarer engineering/business-Kontext | Grober Engineering-Aufwand und Planungszeitraum sichtbar; Absatzvolumen getrennt vom Score |
| Fehlender Preiskontext | Referenzspanne direkt aus lokalen PDF-Grundpreisabschnitten; DE/EUR/MwSt.-Hinweis und Seitenbeleg |
| Audit zu lang / Rohdaten schwer lesbar | Neueste zuerst, Suche, Personentyp, Aktion, Seitenwechsel, ausgewaehltes Ereignis und Vorher/Nachher-Tabelle |
| Kontextverlust beim Zurueckgehen | Szenario in Detail-, Cockpit- und Audit-Links erhalten |
| KI-Antwort verschwindet nach Gegenfrage | Aktualisierung erhaelt das Entscheidungspanel und seine Antwort |
| Evidenz A/B beide als bewiesen bezeichnet | Unterschiedliche Labels Strong/Moderate; keine Behauptung absoluter Sicherheit |
| Unklare Annahmen-Vorschau | Exakt als Entfernen des Zukunftsfaktors bezeichnet; Preview-Chart aktualisiert sich |

## Grenzen, die beim Pitch sichtbar bleiben muessen

- Die gelieferten Optionslisten sind deutsche Referenzen. Ein Angebotstreffer
  bestaetigt keine Verfuegbarkeit in den USA oder China.
- Aufwand S/M/L ist eine vorlaeufige Schaetzung, kein Engineering-Commitment.
- Die Zukunftsfaktor-Vorschau entfernt nicht saemtliche Annahmen; sie prueft
  nur die Abhaengigkeit des Scores von diesem einen Faktor.
- Eine Hash-Kette erkennt nachtraegliche Eingriffe gegen die vorhandene Kette.
  Ohne externen vertrauenswuerdigen Anker verhindert sie kein vollstaendiges
  Umschreiben durch jemanden mit Kontrolle ueber die Datenbank.
- Keine Zeitersparnis, Grounding-Rate oder Produktreife ohne Messung behaupten.
- Bereits vorhandene Demo-Bundles koennen weniger Segment-/Studienkontext
  enthalten als die Rohdaten. Die UI erfindet diese fehlenden Werte nicht.
- Der Discord-Abgleich und die exakte Zuordnung zu den nummerierten
  UI-Screenshots bleiben offen, bis diese Quellen zugaenglich sind.

## Schwerpunkt im Pitch

Ein konkreter Kundenwunsch muss als durchgehende Geschichte funktionieren:
Originalbeleg -> Befund -> messbare Anforderung -> erklaerter Rang ->
Gegenbeleg -> menschliche Entscheidung mit Begruendung -> Audit-Eintrag.
Danach dasselbe Vorgehen fuer ein zweites Modell oder einen anderen Markt.
Der Nutzen ist eine pruefbare Entscheidungsgrundlage fuer den PM. Preise,
Autoanimationen und die Zahl der Menuepunkte sind Nebenpunkte.

Der aktualisierte Klickpfad steht in [pitch/PITCH.md](pitch/PITCH.md).

## Verifikation

- Produktionsbuild mit Next.js 16.4 bestanden; auch Audit und Detailseiten
  werden mit den erforderlichen Suspense-Grenzen erzeugt.
- 29 gezielte Backend-Tests bestanden (Produktreferenz, Views, API).
- Playwright prueft Modell-/Regionsfilter, Anforderungsfilter, Score-Vorschau,
  Szenario-Ruecknavigation und Audit-Filter bei 1440, 768 und 390 Pixeln.
- Ein simulierter Challenge-Response prueft, dass die Antwort nach dem
  erneuten Laden sichtbar bleibt, ohne echte PM-Entscheidungen zu schreiben.
- Screenshots liegen lokal in `outputs/ux-review/` und sind nicht fuer Git
  vorgesehen, da die Ansichten Daten aus den BMW-Unterlagen enthalten koennen.
- Pruefinstanz: Frontend `http://localhost:3001`, Backend `http://localhost:8002`.
  Beide nutzen separate Build-/Audit-Dateien; die regulaeren Ports bleiben frei
  fuer die schon laufenden Instanzen.
