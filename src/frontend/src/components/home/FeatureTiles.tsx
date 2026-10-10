import { Icon, type IconName } from "@/src/components/ui/Icon";
import { Button } from "@/src/components/ui/Button";
import { Reveal } from "@/src/components/ui/Reveal";
import { SectionHeading } from "@/src/components/ui/Typography";

const TILES: { icon: IconName; title: string; text: string; href: string; cta: string }[] = [
  { icon: "list", title: "Ranked list", text: "Every proposal with score, evidence level and conflicts.", href: "/cockpit", cta: "Open list" },
  { icon: "evidence", title: "Evidence trail", text: "Click a row to see the voices, studies and sources behind it.", href: "/cockpit", cta: "See evidence" },
  { icon: "sliders", title: "What-if weights", text: "Change what matters and watch the ranking move.", href: "/cockpit", cta: "Try weights" },
  { icon: "audit", title: "Audit trail", text: "Who decided what, when and why. Nothing is overwritten.", href: "/audit", cta: "Open audit" },
];

export function FeatureTiles() {
  return (
    <section id="features" className="mx-auto max-w-[1400px] px-6 py-24 lg:px-10">
      <Reveal><SectionHeading>Find your requirement.</SectionHeading></Reveal>
      <div className="mt-14 grid gap-px bg-[var(--hairline)] sm:grid-cols-2 lg:grid-cols-4">
        {TILES.map((t, i) => (
          <Reveal key={t.title} delay={i * 80} className="bg-white">
            <article className="flex h-full flex-col p-8">
              <Icon name={t.icon} size={40} />
              <h3 className="mt-8 text-2xl font-light">{t.title}</h3>
              <p className="mt-3 flex-1 text-[var(--grey-500)]">{t.text}</p>
              <div className="mt-8"><Button variant="outline" href={t.href}>{t.cta}</Button></div>
            </article>
          </Reveal>
        ))}
      </div>
    </section>
  );
}
