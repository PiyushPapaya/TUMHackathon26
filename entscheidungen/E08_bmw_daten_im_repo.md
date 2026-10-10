# E08 BMW-Rohdaten liegen im öffentlichen Repo

**Frage:** Lassen wir `data/raw/` im Git, oder nehmen wir es wieder heraus?

## Was ich gefunden habe

- Das Repo `PiyushPapaya/TUMHackathon26` ist **öffentlich**.
- `data/raw/` enthält 9 BMW-Dateien (Feedback-Excel, Kundenstudien, Absatzzahlen, Optionslisten, Briefing). Sie sind getrackt, seit Commit `17727fb`: "bewusste Entscheidung des Leads".
- `CLAUDE.md` und `data/README.md` sagen dagegen: "BMW-Daten nie committen, data/ ist gitignored".
- Das Challenge-Material ist laut Brief vertraulich, wir kennen die Nutzungsbedingungen des Hackathons nicht.

## Optionen

| | Option | Plus | Minus |
|---|---|---|---|
| A | **Drinlassen** | Jeder hat die Daten sofort nach `git pull`. Die Jury-KI kann die Pipeline mit echten Daten nachvollziehen. | Wenn der Hackathon Vertraulichkeit verlangt, verstoßen wir dagegen. Einmal veröffentlicht, bleibt es in der Git-Geschichte. |
| B | **Herausnehmen** (`git rm --cached`, wieder in `.gitignore`), Weitergabe per Drive | Passt zu `CLAUDE.md`. | Die Geschichte enthält die Dateien weiter, Entfernen daraus braucht einen Verlauf-Umbau, der laut Regeln verboten ist. Jeder muss die Daten selbst kopieren. |
| C | Repo auf **privat** stellen bis zur Abgabe | Daten bleiben zugänglich für das Team, nicht öffentlich. | Entire / EHL-Abgabe braucht evtl. ein öffentliches Repo. Prüfen. |

## Empfehlung

**Zuerst klären, nicht raten:** Steht in den Hackathon-Regeln, ob die Daten weitergegeben werden dürfen und ob das Repo öffentlich sein muss? Wenn Vertraulichkeit gilt: **C**, falls die Abgabe ein privates Repo erlaubt, sonst **B** mit Rücksprache bei der Orga. Das ist deine Entscheidung, Piyush. Ich ändere nichts.

## Unsere Entscheidung
**A, drinlassen** (Piyush, Sa 10.10. abends). Das Repo bleibt öffentlich, `data/raw/` bleibt getrackt.
Pipeline-Ergebnisse (`data/processed/`, `data/eval/`, LLM-Cache) bleiben weiter **lokal**, weil sie Kundenzitate in neuer Zusammenstellung enthalten.

## Warum
Die Jury-KI und Fremde sollen die Pipeline mit echten Daten nachbauen können (`python src/backend/pipeline.py --scenario G60-US`). Herausnehmen (B) hilft nicht, weil die Dateien in der Git-Geschichte bleiben und ein Verlauf-Umbau verboten ist.
Verworfen: C (privat), weil unklar ist, ob die EHL-Abgabe und Entire ein privates Repo lesen können.
**Risiko bewusst getragen:** Sagt die Orga, die Daten sind vertraulich, stellt Piyush das Repo sofort auf privat und klärt die Abgabe mit der Orga.
