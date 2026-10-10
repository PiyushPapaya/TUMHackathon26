# Entscheidungs-Log (kleine technische Sachen)

| Datum | Entscheidung | Warum |
|---|---|---|
| 10.10. | Alte Pläne, Skills und Code bleiben unverändert | Es ist Sa 17:00, die Pipeline läuft, 91 Tests sind grün. Umbauen kostet Zeit und bringt Risiko. |
| 10.10. | Entscheidungskarten liegen in `entscheidungen/` im Repo-Root | So steht es im Auftrag, und das Team findet sie sofort. |
| 10.10. | Entscheidungen E01-E08 gelten **vorläufig nach meiner Empfehlung**, bis das Team in den Karten anders entscheidet | Das Team hat noch nicht geantwortet, und die Roadmap darf nicht warten. Jede Karte bleibt offen, bis jemand "Unsere Entscheidung" ausfüllt. |
| 10.10. | Code, `src/frontend/` und `data/` werden nicht verschoben. `app/` und `outputs/` aus dem Vorschlag: `outputs/` neu, `app/` nicht | Verschieben bricht CI, Skills, Entire und die Besitzregeln (Karte E07). |
| 10.10. | `workspace/` heißt jetzt `werkstatt/` (ohne Fabian); Fabians Dateien und drei erledigte Ablaufpläne liegen in `archiv/` | Fabian ist nicht dabei, die Ablaufpläne sind vorbei. Mit `git mv`, damit nichts verloren geht. |
| 10.10. | Neue Ordner (`entscheidungen/`, `missionen/`, `visuals/`, `outputs/`, `werkstatt/`, `archiv/`) sind in `.gitattributes` als `export-ignore` eingetragen | Das Review-Budget der Jury-KI war schon voll (200.000 von 200.000 Zeichen). Neue Doku darf Code nicht verdrängen. |
| 10.10. | Roadmap `docs/06_roadmap.md` nennt Feature-Stopp So 10:00 (wie im Auftrag). Code-Freeze 10:30 und Abgabe 11:30 aus `ZEITPLAN.md` bleiben als Puffer | Alte Planung hatte Feature-Freeze So 08:00. Der Puffer vor 12:00 ist wichtiger als Zeitgewinn. |
| 10.10. | Charts und Diagramme entstehen per Skript (`scripts/make_*.py`), nicht per Hand | Jede Person kann Farben und Titel ändern und neu bauen. PNG und SVG kommen aus derselben Quelle. |
| 10.10. | `outputs/BEISPIEL_anforderungsliste_G60-US.csv` kommt aus den **synthetischen** Beispieldaten | So zeigt `outputs/` das Format, ohne echte BMW-Auswertungen zu veröffentlichen (Karte E08). |
