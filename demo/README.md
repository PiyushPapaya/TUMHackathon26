# Demo und Backup-Plan (Owner: Aditya)

Die Demo darf im Pitch **nie** ausfallen. Darum gibt es vier Rückfallebenen, die So 10:00 geprobt werden.

| Ebene | Was | Wann benutzen |
|---|---|---|
| 1 Live | deployte URL bzw. lokal `uvicorn` + `npm run dev` | Normalfall |
| 2 Offline-Modus | `DEMO_MODUS=true` in `.env` → Backend liest LLM-Antworten aus `demo/cache/` | WLAN oder OpenAI langsam/down |
| 3 Video | 2-Minuten-Aufnahme des Kernflows, lokal auf dem Desktop **und** online | Laptop/App streikt |
| 4 Screenshots | 5 Bilder der Demo-Schritte in `demo/screenshots/`, auch als Folie | alles andere fällt aus |

## Feste Testdaten

- `demo/beispiele/`: 2-3 Eingaben, mit denen die Demo **immer** gezeigt wird (gleiche Eingabe = gleiche Ausgabe).
- Nur veröffentlichen, wenn die Lizenz des Partners das erlaubt; sonst synthetische Daten im selben Format.
- Dieselben Fälle sind Teil des Testsets in `tests/data/`, damit wir wissen, dass sie korrekt laufen.

## So cachen wir LLM-Antworten (Bauplan für `src/backend/llm.py`, ab Samstag)

1. Schlüssel = SHA-256 aus `modell + prompt + eingabe` (als JSON mit sortierten Schlüsseln).
2. Vor jedem OpenAI-Aufruf: Gibt es `demo/cache/<schluessel>.json`? Dann diese Antwort zurückgeben.
3. Sonst OpenAI fragen und die Antwort unter diesem Schlüssel speichern.
4. `DEMO_MODUS=true`: **nie** OpenAI fragen; fehlt der Cache-Eintrag, eine klare Fehlermeldung statt Absturz.
5. Vor der Probe So 10:00 alle Demo-Eingaben einmal live durchlaufen lassen. Damit ist der Cache gefüllt, dann committen.

**Warum so:** Das spart Credits, macht die Demo reproduzierbar (gleiche Antwort in Probe und Pitch) und funktioniert ohne Netz. Der Cache enthält keine Keys, nur Antworten.

## Backup-Video

- Link: [VIDEO-LINK, öffentlich, im Inkognito-Fenster geprüft]
- Aufnahme So 08:30 (Aditya), Schnitt Fabian; max. 2 Minuten, ohne Ton aufnehmen, im Pitch live kommentieren.
- Windows: Win+Alt+R (Xbox Game Bar) · Mac: Cmd+Shift+5.

## Demo-Ablauf (5 Klicks, aus `archiv/docs/SCAFFOLD-PLAENE.md` der gewählten Idee)

1. [ ]
2. [ ]
3. [ ]
4. [ ]
5. [ ]
