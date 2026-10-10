"use client";

import { useState } from "react";

/**
 * Hell/Dunkel-Umschalter oben rechts, auf jeder Seite sichtbar (liegt in layout.tsx).
 * Die Startklasse setzt schon ein kleines Inline-Script in layout.tsx, bevor React
 * überhaupt rendert — der Lese-Zugriff auf document hier im useState-Initializer
 * (statt in einem Effect) übernimmt diesen Stand direkt, ohne einen zweiten Render
 * auszulösen. `suppressHydrationWarning` erlaubt, dass sich das Icon-Zeichen vom
 * serverseitigen "🌙" unterscheidet, falls der Browser bereits Dunkel gespeichert hat.
 */
export function ThemeToggle() {
  const [isDark, setIsDark] = useState(
    () => typeof document !== "undefined" && document.documentElement.classList.contains("dark"),
  );

  function toggle() {
    const next = !isDark;
    setIsDark(next);
    document.documentElement.classList.toggle("dark", next);
    try {
      localStorage.setItem("theme", next ? "dark" : "light");
    } catch {
      // Privater Modus o.ä.: Umschalten funktioniert trotzdem, bleibt nur nicht gespeichert.
    }
  }

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={isDark ? "Switch to light theme" : "Switch to dark theme"}
      title={isDark ? "Switch to light theme" : "Switch to dark theme"}
      className="fixed right-4 top-4 z-50 flex h-9 w-9 items-center justify-center rounded-full border border-zinc-300 bg-white/90 text-base text-zinc-700 shadow-sm backdrop-blur-sm transition hover:bg-zinc-100 dark:border-zinc-700 dark:bg-zinc-900/90 dark:text-zinc-200 dark:hover:bg-zinc-800"
    >
      <span suppressHydrationWarning>{isDark ? "☀" : "🌙"}</span>
    </button>
  );
}
