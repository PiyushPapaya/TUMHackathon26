import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { ShaderBackground } from "@/src/components/ShaderBackground";
import "./globals.css";

/**
 * Setzt die .dark-Klasse, bevor React überhaupt rendert (gespeicherte Wahl, sonst
 * Systemeinstellung). Ohne das würde beim Laden kurz das falsche Theme aufblitzen.
 */
const SET_THEME_BEFORE_PAINT = `(function(){try{var t=localStorage.getItem("theme");if(t==="dark"||(!t&&window.matchMedia("(prefers-color-scheme: dark)").matches)){document.documentElement.classList.add("dark");}}catch(e){}})();`;

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Signal2Spec PM Cockpit",
  description: "Evidence-backed product requirement cockpit for PM decisions.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: SET_THEME_BEFORE_PAINT }} />
      </head>
      <body className="min-h-full flex flex-col">
        <ShaderBackground />
        {children}
      </body>
    </html>
  );
}
