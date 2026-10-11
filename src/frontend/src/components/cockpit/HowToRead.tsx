"use client";

import { useState, useSyncExternalStore } from "react";

const KEY = "respec-howto-hidden";
const STEPS = [
  ["Read the ranking", "Higher score = more customers affected, bigger satisfaction gap and stronger proof."],
  ["Open a row", "See why it ranks there, the original customer quotes and what is still uncertain."],
  ["Decide", "Approve, reject, edit or challenge it with a reason. Every decision goes to the audit trail."],
];

function readHidden() {
  try { return localStorage.getItem(KEY) === "1"; } catch { return false; }
}

// Three-step hint for first-time visitors; it can be hidden, and stays hidden in this browser.
export function HowToRead() {
  // Server render: hidden (no flash); browser: read the remembered choice.
  const remembered = useSyncExternalStore(() => () => {}, readHidden, () => true);
  const [dismissed, setDismissed] = useState(false);
  if (remembered || dismissed) return null;
  function hide() {
    setDismissed(true);
    try { localStorage.setItem(KEY, "1"); } catch { /* private mode: hide for this visit only */ }
  }
  return (
    <section aria-label="How to use this page" className="mb-6 grid gap-4 border-y border-[var(--hairline)] py-4 sm:grid-cols-[1fr_1fr_1fr_auto] sm:items-start">
      {STEPS.map(([title, text], i) => (
        <div key={title} className="flex gap-3">
          <span className="flex h-6 w-6 shrink-0 items-center justify-center bg-[var(--blue)] text-xs font-semibold text-white">{i + 1}</span>
          <p className="text-sm"><b className="block text-[var(--ink)]">{title}</b><span className="text-[var(--grey-500)]">{text}</span></p>
        </div>
      ))}
      <button type="button" onClick={hide} className="min-h-11 justify-self-start px-2 text-sm font-semibold text-[var(--blue)] sm:justify-self-end">Got it</button>
    </section>
  );
}
