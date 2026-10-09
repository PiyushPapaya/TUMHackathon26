#!/bin/sh
# Sicherheitsnetz: blockiert gefährliche Git-Befehle, BEVOR Claude Code sie ausführt.
# Warum: 4 von 5 Teammitgliedern programmieren nicht. Ein versehentliches
# `git push --force` oder ein Commit auf main kann die Arbeit anderer zerstören.
# Claude Code ruft das Skript vor jedem Bash/PowerShell-Befehl auf und gibt den
# Befehl als JSON auf stdin. Exit-Code 2 = blockieren, die Meldung sieht Claude.
# Bewusst nur POSIX-sh (kein jq, kein Python), damit es auf Windows (Git Bash) und Mac läuft.
#
# WICHTIG: Das ist ein Komfort-Netz gegen VERSEHEN, keine Sicherheitsgrenze. Ein Muster-Filter
# lässt sich immer umgehen. Die echte Durchsetzung macht GitHub serverseitig: Ruleset
# "main-nur-piyush-merged" (kein Push/Merge auf main außer Piyush, kein force-push, kein Löschen).

raw=$(cat)
# Inhalte in Anführungszeichen (z. B. Commit-Nachrichten) entfernen, damit eine Nachricht wie
# "kein push --force" keinen Fehlalarm auslöst, Flags NACH der Nachricht aber erkannt werden.
input=$(printf '%s' "$raw" | sed -e 's/\\"[^"\]*\\"//g' -e "s/'[^']*'//g")

# Nur Git-Befehle prüfen; alles andere sofort durchlassen.
case "$raw" in
  *git*) ;;
  *) exit 0 ;;
esac

block() {
  echo "BLOCKIERT durch .claude/hooks/git-schutz.sh: $1" >&2
  echo "Erkläre der Person in einfachen Worten, warum das gefährlich ist, und schlage den sicheren Weg vor (siehe CLAUDE.md, Git-Regeln). Im Zweifel: Piyush holen." >&2
  exit 2
}

has() { printf '%s' "$input" | grep -E -q -- "$1"; }

has 'git[^"&;|]*push[^"&;|]*(--force|--force-with-lease|[[:space:]]-f([[:space:]]|"|$)|[[:space:]]\+[^[:space:]"]+)' \
  && block "force-push überschreibt fremde Arbeit auf GitHub."
has 'git[^"&;|]*reset[^"&;|]*--hard' \
  && block "reset --hard löscht ungespeicherte Arbeit unwiderruflich. Sicherer: git stash."
has 'git[^"&;|]*clean[^"&;|]*-[a-zA-Z]*f' \
  && block "git clean -f löscht Dateien endgültig (auch deine .env)."
has 'git[^"&;|]*--no-verify' \
  && block "--no-verify überspringt die Entire-Hooks; ohne Entire-Checkpoints wird die Abgabe abgelehnt."
has 'git[^"&;|]*branch[^"&;|]*[[:space:]]-D([[:space:]]|"|$)' \
  && block "branch -D löscht einen Branch ohne Rückfrage."
has 'git[^"&;|]*push[^"&;|]*(--delete|[[:space:]]:[^[:space:]"]+)' \
  && block "Branches auf GitHub löschen ist verboten (passiert automatisch nach dem Merge)."
has 'git[^"&;|]*push[^"&;|]*([[:space:]](origin[[:space:]]+)?|:)(HEAD:)?(refs/heads/)?main([[:space:]]|"|$)' \
  && block "Direkt auf main pushen ist verboten. Nur über Pull Request, Piyush merged."
if has 'git[^"&;|]*rebase' && ! has 'git[^"&;|]*rebase[^"&;|]*--(abort|continue)'; then
  block "Rebase schreibt Geschichte um. Wir holen main per 'git merge origin/main' herein."
fi

# Commit oder Merge, während man auf main steht? (z. B. nach 'git switch main' vergessen zu wechseln)
if has 'git[^"&;|]*(commit|merge|cherry-pick)'; then
  branch=$(git branch --show-current 2>/dev/null)
  if [ "$branch" = "main" ]; then
    block "Du stehst auf main. Erst eigenen Branch anlegen: git switch -c <vorname>/<thema>"
  fi
fi

exit 0
