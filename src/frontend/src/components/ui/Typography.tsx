// Kleine Text-Bausteine: Eyebrow (Label) und SectionHeading (helle Überschrift mit Punkt).
export function Eyebrow({ children, light }: { children: React.ReactNode; light?: boolean }) {
  return (
    <p className={`text-xs font-semibold uppercase tracking-[0.16em] ${light ? "text-white/70" : "text-[var(--grey-500)]"}`}>
      {children}
    </p>
  );
}

export function SectionHeading({
  children,
  as: Tag = "h2",
  light,
  className = "",
}: {
  children: React.ReactNode;
  as?: "h1" | "h2" | "h3";
  light?: boolean;
  className?: string;
}) {
  return (
    <Tag className={`text-4xl font-light leading-[1.1] tracking-tight sm:text-5xl ${light ? "text-white" : "text-[var(--ink)]"} ${className}`}>
      {children}
    </Tag>
  );
}
