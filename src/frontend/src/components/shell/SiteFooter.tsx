import Link from "next/link";

const COLUMNS: { title: string; links: { href: string; label: string }[] }[] = [
  {
    title: "Product",
    links: [
      { href: "/#how", label: "How it works" },
      { href: "/#features", label: "What you can do" },
      { href: "/#scenarios", label: "Scenarios" },
    ],
  },
  {
    title: "Cockpit",
    links: [
      { href: "/cockpit", label: "Ranked list" },
      { href: "/overview", label: "Overview" },
      { href: "/audit", label: "Audit trail" },
    ],
  },
  { title: "Docs", links: [{ href: "/guide", label: "Guide" }] },
  { title: "Challenge", links: [{ href: "/#how", label: "BMW: AI for Product Decision Making" }] },
];

export function SiteFooter() {
  return (
    <footer className="bg-[var(--grey-100)]">
      {/* Der BMW-Hinweis "KI-generierte Inhalte" wird bei uns zum echten Produkthinweis. */}
      <div className="border-y border-[var(--hairline)] bg-white">
        <p className="mx-auto max-w-[1400px] px-6 py-4 text-sm text-[var(--grey-500)] lg:px-10">
          <span className="font-semibold text-[var(--ink)]">AI-generated content.</span> Proposals are drafted by AI,
          and every claim cites evidence IDs you can open and check.
        </p>
      </div>
      <div className="mx-auto grid max-w-[1400px] gap-10 px-6 py-14 sm:grid-cols-2 lg:grid-cols-4 lg:px-10">
        {COLUMNS.map((col) => (
          <div key={col.title}>
            <p className="mb-4 text-xs font-semibold uppercase tracking-[0.16em] text-[var(--ink)]">{col.title}</p>
            {col.links.map((l) => (
              <Link key={l.label} href={l.href} className="block py-1.5 text-sm text-[var(--grey-500)] hover:text-[var(--blue)]">
                {l.label}
              </Link>
            ))}
          </div>
        ))}
      </div>
      <p className="mx-auto max-w-[1400px] border-t border-[var(--hairline)] px-6 py-6 text-xs text-[var(--grey-500)] lg:px-10">
        Hackathon prototype for the TUM.ai × EHL BMW challenge. BMW is a trademark of BMW AG.
      </p>
    </footer>
  );
}
