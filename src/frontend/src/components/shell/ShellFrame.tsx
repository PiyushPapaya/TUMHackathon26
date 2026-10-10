"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { SiteHeader } from "./SiteHeader";
import { SiteFooter } from "./SiteFooter";
import { ChatButton } from "./ChatButton";

// Rahmen um jede Seite. Mit ?embed=1 (Guide-Seitenleiste) fehlen Header, Footer und Chat-Knopf,
// sonst würde die Leiste die ganze Seite noch einmal in sich zeigen.
function Frame({ children }: { children: React.ReactNode }) {
  const embed = useSearchParams().get("embed") === "1";
  if (embed) return <>{children}</>;
  return (
    <>
      <SiteHeader />
      {children}
      <SiteFooter />
      <ChatButton />
    </>
  );
}

export function ShellFrame({ children }: { children: React.ReactNode }) {
  // useSearchParams braucht Suspense (Next 16 mit cacheComponents).
  return (
    <Suspense fallback={<>{children}</>}>
      <Frame>{children}</Frame>
    </Suspense>
  );
}
