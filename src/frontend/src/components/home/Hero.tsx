import Link from "next/link";
import { Button } from "@/src/components/ui/Button";
import { Icon, type IconName } from "@/src/components/ui/Icon";
import { MediaImage } from "./MediaImage";
import type { HomeData } from "./useHomeData";

// Die vier Kernfunktionen gleich im ersten Bild, jede ein Direktlink: Die Jury sieht in 5 Sekunden, was das Produkt kann.
const FEATURES: { icon: IconName; title: string; text: string; href: string }[] = [
  { icon: "chat", title: "Ask in your words", text: "AI sets the focus, Python ranks", href: "/cockpit" },
  { icon: "list", title: "Ranked & explained", text: "Score math for every proposal", href: "/cockpit" },
  { icon: "evidence", title: "Evidence traffic light", text: "Proven, weak or assumption", href: "/cockpit" },
  { icon: "audit", title: "Audit trail", text: "Who decided what, and why", href: "/audit" },
];

export function Hero({ data }: { data: HomeData }) {
  const f = data.funnels[data.mainId];
  return (
    <section className="relative flex min-h-screen flex-col justify-end overflow-hidden bg-[var(--black)] text-white">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_70%_30%,#1b2a3f_0%,#0a0a0b_65%)]" aria-hidden="true" />
      <MediaImage src="/media/poster.jpg" alt="" priority />
      <div className="absolute inset-0 bg-gradient-to-t from-black via-black/30 to-black/50" aria-hidden="true" />
      <div className="relative mx-auto w-full max-w-[1400px] px-6 pb-16 pt-40 lg:px-10">
        <h1 className="text-6xl font-extralight leading-[0.95] tracking-tight sm:text-8xl lg:text-[9rem]">Signal2Spec.</h1>
        <p className="mt-6 text-2xl font-light text-white/90 sm:text-3xl">From customer voice to the next BMW.</p>
        <div className="mt-10 flex flex-wrap gap-4">
          <Button href="/cockpit">Open cockpit</Button>
          <Button variant="outline-light" href="#how">See how it works</Button>
        </div>
        <ul className="mt-12 grid max-w-5xl gap-px bg-white/15 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((f) => (
            <li key={f.title} className="bg-black/40 backdrop-blur-sm">
              <Link href={f.href} className="group flex h-full items-start gap-3 p-4 transition-colors hover:bg-white/10">
                <Icon name={f.icon} size={20} className="mt-0.5 shrink-0 text-[var(--m-light)]" />
                <span>
                  <span className="block text-sm font-semibold text-white">{f.title}</span>
                  <span className="mt-0.5 block text-xs text-white/60">{f.text}</span>
                </span>
              </Link>
            </li>
          ))}
        </ul>
        <p className="mt-8 max-w-3xl border-t border-white/20 pt-4 text-xs text-white/70">
          {f
            ? `Scenario ${data.mainId}: ${(data.voices[data.mainId] ?? f.evidence).toLocaleString("en-US")} customer voices · ${f.signals} findings · ${f.requirements} requirements, all from the live backend.`
            : "Live numbers appear when the backend is running."}
        </p>
      </div>
    </section>
  );
}
