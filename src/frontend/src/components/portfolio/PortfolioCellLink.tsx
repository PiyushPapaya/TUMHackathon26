import Link from "next/link";
import type { PortfolioCell } from "@/src/lib/insights";
import { EvidenceBadge } from "@/src/components/badges";

// Eine Zelle in Portfolio-Tabelle und Marktvergleich: Rang, Evidenzstufe und Titel, Klick öffnet die Anforderung.
export function PortfolioCellLink({ cell }: { cell: PortfolioCell | null }) {
  if (!cell) return <span className="text-[var(--grey-500)]">–</span>;
  return (
    <Link href={`/requirements/${cell.requirement_id}`} className="block hover:text-[var(--blue)]">
      <span className="flex items-center gap-2">
        <span className="text-2xl font-light tabular-nums">{cell.rank}</span>
        <EvidenceBadge level={cell.evidence_level} />
      </span>
      <span className="mt-1 line-clamp-2 block text-xs text-[var(--grey-500)]">{cell.title}</span>
    </Link>
  );
}
