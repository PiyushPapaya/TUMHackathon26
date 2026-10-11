import Link from "next/link";
import { Icon } from "@/src/components/ui/Icon";
import { Reveal } from "@/src/components/ui/Reveal";
import { SectionHeading } from "@/src/components/ui/Typography";
import { MediaImage } from "./MediaImage";

const LINKS = [
  ["/audit", "Audit trail"],
  ["/guide", "Guide"],
];

export function SplitSection() {
  return (
    <section className="grid md:grid-cols-2">
      <div className="relative min-h-[50vh] bg-[radial-gradient(ellipse_at_30%_60%,#2a2318_0%,#0a0a0b_75%)]">
        <MediaImage src="/media/split.jpg" alt="" sizes="(min-width: 768px) 50vw, 100vw" />
      </div>
      <Reveal className="flex flex-col justify-center bg-[var(--grey-100)] px-6 py-20 lg:px-16">
        <SectionHeading>Every decision leaves a trail.</SectionHeading>
        <p className="mt-6 max-w-md text-[var(--grey-500)]">
          Approve, reject, edit or challenge a proposal. Each step is stored with person, time and reason, so the next review starts from facts.
        </p>
        <div className="mt-8 grid gap-3">
          {LINKS.map(([href, label]) => (
            <Link key={href} href={href} className="inline-flex items-center gap-2 text-[var(--ink)] hover:text-[var(--blue)]">
              {label} <Icon name="chevron" size={16} />
            </Link>
          ))}
        </div>
      </Reveal>
    </section>
  );
}
