"use client";

import { useState } from "react";
import { Icon } from "@/src/components/ui/Icon";

// Schwebender Knopf wie bei BMW. Er öffnet die Guide-Seite als Seitenleiste.
// Bewusst kein erfundener KI-Chat: nur echte Hilfe, die es schon gibt.
export function ChatButton() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        type="button"
        aria-label={open ? "Close guide" : "Open guide"}
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center bg-[var(--blue)] text-white hover:bg-[var(--blue-hover)]"
      >
        <Icon name={open ? "close" : "chat"} />
      </button>
      {open && (
        <aside
          aria-label="Guide"
          className="fixed bottom-0 right-0 top-0 z-40 w-full max-w-md border-l border-[var(--hairline)] bg-white"
        >
          <iframe title="Signal2Spec guide" src="/guide?embed=1" className="h-full w-full" />
        </aside>
      )}
    </>
  );
}
