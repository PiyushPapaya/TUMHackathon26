# Eval-Report G70-EU

Erzeugt mit `python tests/eval/run_eval.py G70-EU`. Nur Zahlen, keine BMW-Zitate (öffentliches Repo).

## Trichter

154 Belege (davon 19 Kommentare im Umfang) -> 11 Befunde
-> 4 Anforderungen.

## Die Zahlen

| Messung | Ergebnis | Ziel |
|---|---|---|
| Grounding Befunde: zitierte Beleg-IDs, die existieren | 100.0 % | 100 % |
| Grounding Anforderungen: zitierte Befund-IDs, die existieren | 100.0 % | 100 % |
| Wortlaut: zitierte Kommentare, wörtlich in der Excel | n/a | 100 % |
| Befund-Treue: "passt" (0 von 0 gelabelt) | n/a | >= 80 % |
| Abdeckung: Kommentare in mindestens einem Befund | 0.0 % | Orientierung |
| Anforderungen mit Zahl im Akzeptanzkriterium | 100.0 % | >= 80 % |

## Methode

- **Grounding/Wortlaut:** automatisch aus den erzeugten Dateien und der Original-Excel, jede ID einzeln geprüft.
- **Befund-Treue:** 50 zufällige Paare (Befund, zitierter Beleg), Seed 42, mit j/n gelabelt
  ("belegt der Kommentar die Aussage des Befunds?"). Ablauf offen benannt: Claude schlug pro Paar j/n mit
  Begründung vor, ein Teammitglied (Aditya) prüfte die Liste und bestätigte sie; die Zahl stammt also nicht
  allein von der KI, ist aber auch kein blindes Menschenurteil. Ein zweiter Durchlauf (KI-Vorlabel, von Lasse
  alle 50 Zeilen geprüft und bestätigt) kam ebenfalls auf 88 %, mit teils anderen Nein-Fällen.
- **Abdeckung:** Kommentare im Umfang (ohne Werkstattfälle), die zu einer Gruppe eines ausgegebenen Befunds gehören.
- **Akzeptanzkriterium mit Zahl:** mindestens eine Ziffer im Text. Das ist ein Näherungswert für "messbar".

## Grenzen

- 50 Paare, Menschen prüften KI-Vorschläge (kein Blind-Label): grobe Größenordnung, kein Konfidenzintervall.
- Befund-Treue mit KI-Vorschlag: Ankereffekt möglich; blindes Zweitlabel durch einen Menschen wäre der nächste
  Schritt.
- Grounding sagt, dass Quellen existieren, nicht dass die Schlussfolgerung richtig ist; dafür ist die Befund-Treue da.
- "Zahl im Kriterium" prüft nicht, ob die Zahl sinnvoll ist.
- Abdeckung < 100 % ist gewollt: Themen ohne BMW-Zuordnung und Gruppen unter 5 Nennungen fallen bewusst weg.
