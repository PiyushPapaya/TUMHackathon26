"use client";

import { useState } from "react";

/**
 * Hell/Dunkel-Umschalter, sitzt in der Top-Bar (src/frontend/app/page.tsx) hinter
 * dem CSV-Export-Button. Die Startklasse setzt schon ein kleines Inline-Script in
 * layout.tsx, bevor React überhaupt rendert — der Lese-Zugriff auf document hier
 * im useState-Initializer (statt in einem Effect) übernimmt diesen Stand direkt,
 * ohne einen zweiten Render auszulösen. `suppressHydrationWarning` erlaubt, dass
 * sich das Icon-Zeichen vom serverseitigen "🌙" unterscheidet, falls der Browser
 * bereits Dunkel gespeichert hat.
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
      className="flex h-9 w-9 items-center justify-center rounded-full border border-zinc-300 bg-surface text-base text-zinc-700 shadow-sm transition hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-200 dark:hover:bg-zinc-800"
      suppressHydrationWarning
    >
      <span suppressHydrationWarning>{isDark ? "☀" : "🌙"}</span>
    </button>
  );
}
