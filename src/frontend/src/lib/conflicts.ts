// Widersprüche einer Anforderung, gleiche Regel wie die Detailseite (core/views.py explain):
// nur Paare, bei denen BEIDE Befunde zitiert sind. Sonst zeigt die Liste ein "!", die Detailseite aber nichts.
type ConflictSignal = { id: string; title: string; conflicts_with: string[] };

export function conflictTitlesFor(signalIds: string[], signalById: Map<string, ConflictSignal>): string[] {
  const cited = new Set(signalIds);
  const pairs = new Set<string>();
  for (const id of signalIds) {
    for (const other of signalById.get(id)?.conflicts_with ?? []) {
      if (cited.has(other)) pairs.add([id, other].sort().join("|"));
    }
  }
  return [...pairs].sort().map((pair) => {
    const [a, b] = pair.split("|");
    return `${signalById.get(a)?.title ?? a} ↔ ${signalById.get(b)?.title ?? b}`;
  });
}
