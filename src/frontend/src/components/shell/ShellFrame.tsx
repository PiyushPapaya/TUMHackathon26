"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { SiteHeader } from "./SiteHeader";
import { SiteFooter } from "./SiteFooter";
import { AssistantProvider } from "./assistant/AssistantProvider";

// Rahmen um jede Seite: Header, Footer und der Assistent (Chat + Guide) unten rechts.
// ?embed=1 zeigt nur den Inhalt (für eingebettete Ansichten ohne Rahmen).
function Frame({ children }: { children: React.ReactNode }) {
  const embed = useSearchParams().get("embed") === "1";
  if (embed) return <>{children}</>;
  return (
    <AssistantProvider>
      <SiteHeader />
      {children}
      <SiteFooter />
    </AssistantProvider>
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
