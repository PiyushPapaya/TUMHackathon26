"use client";

// Lädt GSAP (ScrollTrigger) und Lenis erst auf der Startseite per dynamic import.
// Warum: Das Cockpit ist ein Datenwerkzeug mit nativem Scrollen und soll leicht bleiben.
type Engine = {
  gsap: typeof import("gsap").gsap;
  ScrollTrigger: typeof import("gsap/ScrollTrigger").ScrollTrigger;
};

let pending: Promise<Engine> | null = null;
let users = 0;
let teardown: (() => void) | null = null;

export function acquireScrollEngine(): Promise<Engine> {
  users += 1;
  if (!pending) {
    pending = (async () => {
      const [{ gsap }, { ScrollTrigger }, { default: Lenis }] = await Promise.all([
        import("gsap"),
        import("gsap/ScrollTrigger"),
        import("lenis"),
      ]);
      gsap.registerPlugin(ScrollTrigger);
      const lenis = new Lenis({ lerp: 0.1 });
      lenis.on("scroll", ScrollTrigger.update);
      const tick = (time: number) => lenis.raf(time * 1000);
      gsap.ticker.add(tick);
      gsap.ticker.lagSmoothing(0);
      teardown = () => {
        gsap.ticker.remove(tick);
        lenis.destroy();
      };
      return { gsap, ScrollTrigger };
    })();
  }
  return pending;
}

export function releaseScrollEngine() {
  users -= 1;
  if (users <= 0) {
    teardown?.();
    teardown = null;
    pending = null;
    users = 0;
  }
}
