# Git-Hilfe: die 8 Situationen, die am Wochenende passieren

Du musst diese Befehle nicht tippen. Sag Claude den Satz in **fett**, und Claude erklärt und führt aus. Die Befehle stehen hier, damit du verstehst, was passiert.

## 1. „Hol dir den neuesten Stand und leg meinen Branch an.“

```bash
git switch main          # auf den Haupt-Branch wechseln
git pull                 # neueste Änderungen holen
git switch -c lasse/login-seite   # eigenen Branch anlegen
```

## 2. „Speicher meine Arbeit.“

```bash
git status               # was hat sich geändert?
git add src/frontend/app/login/page.tsx   # gezielt Dateien auswählen, nicht blind "git add ."
git commit -m "Login-Seite gebaut, weil Nutzer sich vor dem Upload anmelden müssen"
```

## 3. „Schick das zu GitHub und mach einen Pull Request.“

```bash
git push -u origin lasse/login-seite
gh pr create --base main --reviewer PiyushPapaya --fill
```

Danach: Link an Piyush schicken. **Nicht selbst mergen** (geht auch gar nicht, das Ruleset verhindert es).

## 4. „Hol die neuen Änderungen von main in meinen Branch.“

```bash
git fetch origin
git merge origin/main
```

Wir nehmen **merge statt rebase**, weil merge nie Geschichte umschreibt und nie einen force-push braucht.

## 5. „Ich habe einen Merge-Konflikt, erklär ihn mir.“

Git markiert die Stelle so:

```text
<<<<<<< HEAD
deine Version
=======
die Version aus main
>>>>>>> origin/main
```

Claude zeigt dir beide Versionen, erklärt sie und **fragt**, welche gelten soll. Bei Code anderer Leute: **Piyush holen.** Abbrechen geht jederzeit mit `git merge --abort`.

## 6. „Ich habe auf main gearbeitet, aus Versehen.“

Kein Problem, solange nicht gepusht (Pushen auf main geht sowieso nicht):

```bash
git switch -c lasse/rettung    # nimmt deine Änderungen mit auf einen neuen Branch
```

## 7. „Ich will meine letzten Änderungen verwerfen.“

Erst sichern, dann verwerfen:

```bash
git stash                # legt Änderungen beiseite (wiederherstellbar mit git stash pop)
```

**Verboten:** `git reset --hard`, `git push --force`, `git clean -f`, `git rebase`, Branches löschen. Der Git-Schutz-Hook (`.claude/hooks/git-schutz.sh`) blockiert sie.

## 8. „Der Commit hängt / Entire meckert.“

- Hängt der Commit? Prüfen, ob `.entire/settings.json` `"commit_linking": "always"` enthält (ist im Repo). Dann `entire doctor`.
- „Entire CLI is enabled but not installed or not on PATH“: Entire installieren ([OPENAI-UND-ENTIRE.md](OPENAI-UND-ENTIRE.md)), Terminal neu öffnen.
- Checkpoints auf GitHub? `git ls-remote origin 'refs/entire/checkpoints/*'`

## Merksätze

- Ein Commit = ein logischer Schritt. Die Nachricht sagt **was und warum**, auf Deutsch.
- Alle 1-2 Stunden ein kleiner PR. Große PRs erzeugen Konflikte.
- Nur in **deinem** Ordner und **deinem** `werkstatt/<name>/` arbeiten.
