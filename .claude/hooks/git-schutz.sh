#!/bin/sh
# Sicherheitsnetz: blockiert gefährliche Git-Befehle, BEVOR Claude Code sie ausführt.
# Warum: 4 von 5 Teammitgliedern programmieren nicht. Ein versehentliches
# `git push --force` oder ein Commit auf main kann die Arbeit anderer zerstören.
# Claude Code ruft das Skript vor jedem Bash/PowerShell-Befehl auf und gibt den
# Befehl als JSON auf stdin. Exit-Code 2 = blockieren, die Meldung sieht Claude.
# Bewusst nur POSIX-sh + sed -E (kein jq, kein Python), damit es auf Windows (Git Bash) und Mac läuft.
#
# WICHTIG: Das ist ein Komfort-Netz gegen VERSEHEN, keine Sicherheitsgrenze. Ein Muster-Filter
# lässt sich mit Absicht immer umgehen (Aliase, Variablen …). Die echte Durchsetzung macht GitHub
# serverseitig: Ruleset "main-nur-piyush-merged" (kein Push/Merge auf main außer Piyush,
# kein force-push, kein Löschen von main).

raw=$(cat)

# Schnellweg: ohne "git" im Befehl nichts zu prüfen.
case "$raw" in
  *git*) ;;
  *) exit 0 ;;
esac

# 1) Nur den Wert von "command" aus dem JSON nehmen (nicht "description" usw.)
#    und die JSON-Escapes \" und \\ zurückwandeln.
cmd=$(printf '%s' "$raw" \
  | sed -E 's/.*"command"[[:space:]]*:[[:space:]]*"(([^"\\]|\\.)*)".*/\1/' \
  | sed -e 's/\\"/"/g' -e 's/\\\\/\\/g')

# 2) Nur die Commit-NACHRICHT entfernen, damit "kein push --force" im Text keinen Fehlalarm
#    auslöst. Alle anderen Argumente (auch in Anführungszeichen, z. B. "--force") bleiben drin.
cmd=$(printf '%s' "$cmd" \
  | sed -E "s/(-m|--message)(=|[[:space:]]+)\"[^\"]*\"//g; s/(-m|--message)(=|[[:space:]]+)'[^']*'//g")

block() {
  echo "BLOCKIERT durch .claude/hooks/git-schutz.sh: $1" >&2
  echo "Erkläre der Person in einfachen Worten, warum das gefährlich ist, und schlage den sicheren Weg vor (siehe CLAUDE.md, Git-Regeln). Im Zweifel: Piyush holen." >&2
  exit 2
}

# Prüft innerhalb EINES Befehlsteils (getrennt durch && ; |); Anführungszeichen werden ignoriert.
has() { printf '%s' "$cmd" | tr -d "\"'" | grep -E -q -- "$1"; }
S='[^&;|]*'

has "git${S}push${S}(--force|--force-with-lease|[[:space:]]-f([[:space:]]|\$)|[[:space:]]\+[^[:space:]]+)" \
  && block "force-push überschreibt fremde Arbeit auf GitHub."
has "git${S}reset${S}--hard" \
  && block "reset --hard löscht ungespeicherte Arbeit unwiderruflich. Sicherer: git stash."
has "git${S}clean${S}[[:space:]]-[a-zA-Z]*f" \
  && block "git clean -f löscht Dateien endgültig (auch deine .env)."
has "git${S}--no-verify" \
  && block "--no-verify überspringt die Entire-Hooks; ohne Entire-Checkpoints wird die Abgabe abgelehnt."
has "git${S}branch${S}[[:space:]]-D([[:space:]]|\$)" \
  && block "branch -D löscht einen Branch ohne Rückfrage."
has "git${S}push${S}(--delete|[[:space:]]:[^[:space:]]+)" \
  && block "Branches auf GitHub löschen ist verboten (passiert automatisch nach dem Merge)."
has "git${S}push${S}([[:space:]]|:)(HEAD:)?(refs/heads/)?main([[:space:]]|\$)" \
  && block "Direkt auf main pushen ist verboten. Nur über Pull Request, Piyush merged."
if has "git${S}rebase" && ! has "git${S}rebase${S}--(abort|continue)"; then
  block "Rebase schreibt Geschichte um. Wir holen main per 'git merge origin/main' herein."
fi

# Commit oder Merge, während man auf main steht? (z. B. nach 'git switch main' vergessen zu wechseln)
if has "git${S}(commit|merge|cherry-pick)"; then
  branch=$(git branch --show-current 2>/dev/null)
  if [ "$branch" = "main" ]; then
    block "Du stehst auf main. Erst eigenen Branch anlegen: git switch -c <vorname>/<thema>"
  fi
fi

exit 0
