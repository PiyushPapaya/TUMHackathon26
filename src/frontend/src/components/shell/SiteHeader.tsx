"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { getScenarios, type Scenario } from "@/src/lib/api";
import { Logo } from "@/src/components/ui/Logo";
import { MStripe } from "@/src/components/ui/MStripe";
import { Icon } from "@/src/components/ui/Icon";
import { DEFAULT_SCENARIO_ID, scenarioLabel } from "./scenarioLabel";

// Model selection, decisions, comparison and history are the primary PM destinations.
const NAV = [
  { href: "/models", label: "Models" },
  { href: "/cockpit", label: "Cockpit" },
  { href: "/portfolio", label: "Compare" },
  { href: "/audit", label: "Audit trail" },
];

// Seiten, die ein Szenario in ?scenario= verstehen. Das Szenario-Menü bleibt auf der Seite, statt ins Cockpit zu springen.
const SCENARIO_PAGES = ["/cockpit", "/insights", "/evidence", "/audit"];

// Nur das Cockpit braucht ein Szenario. Der Audit-Trail startet bewusst mit "All scenarios",
// damit PMs zuerst die ganze Entscheidungshistorie sehen und dann selbst filtern.
function navHref(href: string, scenarioId: string) {
  return href === "/cockpit" ? `${href}?scenario=${scenarioId}` : href;
}

export function SiteHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const params = useSearchParams();
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  // Wir merken die Route, bei der das Menü geöffnet wurde: Routenwechsel schließt es automatisch,
  // ohne setState im Effect.
  const [mobilePath, setMobilePath] = useState<string | null>(null);
  const mobileOpen = mobilePath === pathname;
  const setMobileOpen = (open: boolean | ((v: boolean) => boolean)) =>
    setMobilePath((cur) => ((typeof open === "function" ? open(cur === pathname) : open) ? pathname : null));
  const [scrolled, setScrolled] = useState(false);

  const isHome = pathname === "/";
  // Auf der Startseite liegt der Header transparent über dem schwarzen Hero.
  const light = isHome && !scrolled && !mobileOpen;
  // Das Szenario steckt in der URL (?scenario=), so teilen Header, Cockpit und Menü denselben Zustand.
  const scenarioId = params.get("scenario") ?? DEFAULT_SCENARIO_ID;

  useEffect(() => {
    getScenarios().then(setScenarios).catch(() => setScenarios([]));
  }, []);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setMobilePath(null);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const textCls = light ? "text-white" : "text-[var(--ink)]";

  return (
    <>
      <header
        className={`fixed inset-x-0 top-0 z-40 transition-colors duration-300 ${
          light ? "bg-transparent" : "border-b border-[var(--hairline)] bg-white"
        }`}
      >
        <div className="mx-auto flex h-[72px] max-w-[1400px] items-center justify-between gap-6 px-6 lg:px-10">
          <Link href="/" aria-label="Signal2Spec home"><Logo light={light} /></Link>

          <nav className="hidden items-center gap-6 xl:gap-8 lg:flex" aria-label="Main">
            {NAV.map((item) => {
              const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.href}
                  href={navHref(item.href, scenarioId)}
                  aria-current={active ? "page" : undefined}
                  className={`relative py-6 text-[15px] ${textCls} ${active ? "font-semibold" : ""} hover:text-[var(--blue)]`}
                >
                  {item.label}
                  {active && <span className="absolute inset-x-0 bottom-3 h-[2px] bg-[var(--blue)]" />}
                </Link>
              );
            })}
          </nav>

          <div className="flex items-center gap-3">
            {scenarios.length > 0 && (
              <select
                aria-label="Scenario"
                value={scenarioId}
                onChange={(e) => router.push(`${SCENARIO_PAGES.includes(pathname) ? pathname : "/cockpit"}?scenario=${e.target.value}`)}
                className={`hidden h-10 border bg-transparent px-3 text-sm md:block ${
                  light ? "border-white/60 text-white" : "border-[var(--hairline)] text-[var(--ink)]"
                }`}
              >
                {scenarios.map((s) => (
                  <option key={s.id} value={s.id} className="text-[var(--ink)]">{scenarioLabel(s)}</option>
                ))}
              </select>
            )}
            <button
              type="button"
              aria-label={mobileOpen ? "Close menu" : "Open menu"}
              aria-expanded={mobileOpen}
              onClick={() => setMobileOpen((v) => !v)}
              className={`flex h-10 w-10 items-center justify-center lg:hidden ${textCls}`}
            >
              <Icon name={mobileOpen ? "close" : "menu"} />
            </button>
          </div>
        </div>
        <MStripe />
        {mobileOpen && (
          <nav className="border-t border-[var(--hairline)] bg-white px-6 py-4 lg:hidden" aria-label="Mobile">
            {NAV.map((item) => (
              <Link key={item.href} href={navHref(item.href, scenarioId)} className="block py-3 text-lg text-[var(--ink)]">{item.label}</Link>
            ))}
            {scenarios.map((s) => (
              <Link key={s.id} href={`/cockpit?scenario=${s.id}`} className="block py-2 text-sm text-[var(--grey-500)]">
                {scenarioLabel(s)}
              </Link>
            ))}
          </nav>
        )}
      </header>
      {/* Platzhalter, damit Unterseiten nicht unter dem festen Header liegen. Die Startseite startet bündig. */}
      {!isHome && <div className="h-[75px]" aria-hidden="true" />}
    </>
  );
}
