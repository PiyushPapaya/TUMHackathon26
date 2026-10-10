// Karte nur mit 1 px Linie, ohne Schatten und Rundung.
export function HairlineCard({
  children,
  className = "",
  as: Tag = "section",
}: {
  children: React.ReactNode;
  className?: string;
  as?: "section" | "div" | "article";
}) {
  return <Tag className={`border border-[var(--hairline)] bg-white p-6 ${className}`}>{children}</Tag>;
}
