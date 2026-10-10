import type { Metadata } from "next";
import { Archivo } from "next/font/google";
import farben from "@/baukasten/farben.json";
import { StudioDataProvider } from "@/src/studio/StudioData";
import { StudioNav } from "@/src/studio/StudioNav";
import "./studio.css";

/**
 * Rahmen der Werkbank (/studio): eigene Schrift, Farben aus dem Baukasten, gemeinsame Daten.
 * Eigenes Layout statt Änderungen an app/layout.tsx, weil das Cockpit (Pfad D) Lasse gehört.
 * Archivo mit Breiten-Achse: breite Überschriften erinnern an Typenschilder im Auto, ohne Logo.
 */
const archivo = Archivo({ subsets: ["latin"], axes: ["wdth"], variable: "--font-archivo" });

export const metadata: Metadata = {
  title: "Signal2Spec · Workbench",
  description: "Test the requirement list before you sign it off.",
};

export default function StudioLayout({ children }: LayoutProps<"/studio">) {
  const palette = {
    "--ink": farben.ink,
    "--paper": farben.paper,
    "--accent": farben.accent,
    "--praise": farben.praise,
    "--complaint": farben.complaint,
    "--assumption": farben.assumption,
  } as React.CSSProperties;

  return (
    <div
      style={{ ...palette, fontFamily: "var(--font-archivo), system-ui, sans-serif" }}
      className={`${archivo.variable} min-h-screen bg-[var(--paper)] text-[var(--ink)]`}
    >
      <StudioDataProvider>
        <StudioNav />
        <main className="mx-auto max-w-6xl px-4 pb-24 pt-10 sm:px-8">{children}</main>
      </StudioDataProvider>
    </div>
  );
}
