import { Button } from "@/src/components/ui/Button";
import { MediaImage } from "./MediaImage";
import type { HomeData } from "./useHomeData";

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
        <p className="mt-12 max-w-3xl border-t border-white/20 pt-4 text-xs text-white/70">
          {f
            ? `Scenario ${data.mainId}: ${f.evidence.toLocaleString("en-US")} customer voices · ${f.signals} findings · ${f.requirements} requirements, all from the live backend.`
            : "Live numbers appear when the backend is running."}
        </p>
      </div>
    </section>
  );
}
