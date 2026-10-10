# Eval-Report G60-US

Erzeugt mit `python tests/eval/run_eval.py G60-US`. Nur Zahlen, keine BMW-Zitate (öffentliches Repo).

## Trichter

3713 Belege (davon 3481 Kommentare im Umfang) -> 45 Befunde
-> 0 Anforderungen.

## Die Zahlen

| Messung | Ergebnis | Ziel |
|---|---|---|
| Grounding Befunde: zitierte Beleg-IDs, die existieren | 100.0 % | 100 % |
| Grounding Anforderungen: zitierte Befund-IDs, die existieren | n/a | 100 % |
| Wortlaut: zitierte Kommentare, wörtlich in der Excel | 100.0 % | 100 % |
| Befund-Treue: "passt" (0 von 50 gelabelt) | n/a | >= 80 % |
| Abdeckung: Kommentare in mindestens einem Befund | 41.8 % | Orientierung |
| Anforderungen mit Zahl im Akzeptanzkriterium | n/a | >= 80 % |

## Methode

- **Grounding/Wortlaut:** automatisch aus den erzeugten Dateien und der Original-Excel, jede ID einzeln geprüft.
- **Befund-Treue:** 50 zufällige Paare (Befund, zitierter Beleg), Seed 42, von einem Teammitglied mit j/n gelabelt
  ("belegt der Kommentar die Aussage des Befunds?"). Nicht per KI, sonst prüft die KI sich selbst.
- **Abdeckung:** Kommentare im Umfang (ohne Werkstattfälle), die zu einer Gruppe eines ausgegebenen Befunds gehören.
- **Akzeptanzkriterium mit Zahl:** mindestens eine Ziffer im Text. Das ist ein Näherungswert für "messbar".

## Grenzen

- Stichprobe von 50 Paaren, ein Labler: grobe Größenordnung, kein Konfidenzintervall.
- Grounding sagt, dass Quellen existieren, nicht dass die Schlussfolgerung richtig ist; dafür ist die Befund-Treue da.
- "Zahl im Kriterium" prüft nicht, ob die Zahl sinnvoll ist.
- Abdeckung < 100 % ist gewollt: Themen ohne BMW-Zuordnung und Gruppen unter 5 Nennungen fallen bewusst weg.
