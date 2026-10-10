# FAQ fürs Team

**Wo fange ich an?**
Claude Code im Repo-Ordner starten und sagen: „Starte meine Sitzung.“ Das löst den Skill `sitzung-start` aus.

**Was muss ich heute Abend (Fr) noch tun?**
[docs/SETUP.md](../SETUP.md) komplett durchgehen: Git, gh, Claude Code, Entire, Repo klonen, `entire enable --agent claude-code`, `.env` mit OpenAI-Key. Discord beitreten (discord.gg/4UDNd5TAg). Den eigenen GitHub-Usernamen an Piyush schicken, falls noch nicht geschehen.

**Wann wird die Challenge gewählt?**
Reveal Sa 10:00, Deep Dives 12:00, **Wahl bis Sa 13:00** durch den Captain (Piyush) auf ehl.gg. Bis dahin änderbar. Alle müssen vorher eingecheckt sein (09:00-10:00).

**Darf ich in einen fremden Ordner schreiben?**
Nein. Lesen ja. Brauchst du dort etwas: Issue oder PR-Kommentar an den Owner. Die Tabelle steht in [CLAUDE.md](../../CLAUDE.md).

**Wohin mit Notizen, Prompts, Experimenten?**
In `workspace/<dein-name>/`. Dort darfst du alles, und es landet nicht im Abgabe-Snapshot.

**Ich will eine neue Bibliothek benutzen.**
Im PR beantragen („Neue Dependency: X, weil …“), Piyush entscheidet. Nicht selbst installieren und committen.

**Mein PR wird nicht gemerged.**
Prüfen: Ist die CI grün? Hat Piyush approved? Gibt es Konflikte mit main? Dann Piyush anpingen. Mergen kann **nur** Piyush (Ruleset `main-nur-piyush-merged`).

**Warum darf ich nicht direkt auf main?**
Weil der Stand von `main` beim Klick auf „Submit“ bewertet wird. Ein kaputter Push kurz vor der Deadline kostet den Sieg.

**Was ist Ownership-Sprache und warum so wichtig?**
„Wir nehmen X, weil …; Y verworfen, weil …“. Entire zeichnet unsere Prompts auf, und ein KI-Reviewer bewertet sie. 35 % davon zählt, ob **wir** entscheiden oder nur die KI erzählen lassen.
- Gut: „Wir speichern die Ergebnisse als JSON statt in einer Datenbank, weil wir in 24 h keine Migrationen pflegen wollen.“
- Schlecht: „Mach mal eine Datenbank.“

**Darf ich ChatGPT/Claude den ganzen Code schreiben lassen?**
Ja, KI ist ausdrücklich erwünscht. Aber du musst erklären können, was der Code tut. Die Jury fragt jede Person.

**Was passiert bei einem geleakten API-Key?**
Sofort beim Anbieter widerrufen, neuen erzeugen, Piyush Bescheid geben. Nicht nur die Datei löschen, denn der Key bleibt in der Git-Historie.

**Wie lange ist der Pitch?**
**6 Minuten inklusive Fragen**, strikt. Plan: ~3:30 Pitch mit Live-Demo, ~2:30 Fragen. Details in [PITCH.md](../pitch/PITCH.md).

**Was zählt mehr: Code oder Pitch?**
Die Platzierung macht die menschliche Jury. Der KI-Report ist ihre Lesehilfe. Beides muss stimmen, aber eine funktionierende Demo mit einer harten Zahl schlägt perfekten Code ([VERGANGENE-PROJEKTE.md](VERGANGENE-PROJEKTE.md)).

**Dürfen wir schlafen?**
Ja, in Schichten (siehe [ZEITPLAN.md](../ZEITPLAN.md)). Übernachten vor Ort ist erlaubt.

**Wer ist Ansprechpartner bei Orga-Fragen?**
Discord (discord.gg/4UDNd5TAg) oder makeathon@tum-ai.com.
