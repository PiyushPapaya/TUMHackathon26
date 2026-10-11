# Eval-Report G60-EU

Erzeugt mit `python tests/eval/run_eval.py G60-EU`. Nur Zahlen, keine BMW-Zitate (öffentliches Repo).

## Trichter

148 Belege (davon 111 Kommentare im Umfang) -> 10 Befunde
-> 10 Anforderungen.

## Die Zahlen

| Messung | Ergebnis | Ziel |
|---|---|---|
| Grounding Befunde: zitierte Beleg-IDs, die existieren | 100.0 % | 100 % |
| Grounding Anforderungen: zitierte Befund-IDs, die existieren | 100.0 % | 100 % |
| Wortlaut: zitierte Kommentare, wörtlich in der Excel | 100.0 % | 100 % |
| Befund-Treue: "passt" (0 von 0 gelabelt) | n/a | >= 80 % |
| Abdeckung: Kommentare in mindestens einem Befund | 50.5 % | Orientierung |
| Anforderungen mit Zahl im Akzeptanzkriterium | 100.0 % | >= 80 % |

## Methode

- **Grounding/Wortlaut:** automatisch aus den erzeugten Dateien und der Original-Excel, jede ID einzeln geprüft.
- **Befund-Treue:** 50 zufällige Paare (Befund, zitierter Beleg), Seed 42, mit j/n gelabelt
  ("belegt der Kommentar die Aussage des Befunds?"). Ablauf offen benannt: Claude schlug pro Paar j/n mit
  Begründung vor, ein Teammitglied (Aditya) prüfte die Liste und bestätigte sie; die Zahl stammt also nicht
  allein von der KI, ist aber auch kein blindes Menschenurteil. Ein zweiter, reiner KI-Durchlauf (Lasse, ohne
  menschliche Prüfung) kam ebenfalls auf 88 %, mit teils anderen Nein-Fällen.
- **Abdeckung:** Kommentare im Umfang (ohne Werkstattfälle), die zu einer Gruppe eines ausgegebenen Befunds gehören.
- **Akzeptanzkriterium mit Zahl:** mindestens eine Ziffer im Text. Das ist ein Näherungswert für "messbar".

## Grenzen

- Stichprobe von 50 Paaren, ein Labler: grobe Größenordnung, kein Konfidenzintervall.
- Befund-Treue mit KI-Vorschlag: Ankereffekt möglich; blindes Zweitlabel durch einen Menschen wäre der nächste
  Schritt.
- Grounding sagt, dass Quellen existieren, nicht dass die Schlussfolgerung richtig ist; dafür ist die Befund-Treue da.
- "Zahl im Kriterium" prüft nicht, ob die Zahl sinnvoll ist.
- Abdeckung < 100 % ist gewollt: Themen ohne BMW-Zuordnung und Gruppen unter 5 Nennungen fallen bewusst weg.
