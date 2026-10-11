import type { Metadata } from "next";
import { Hanken_Grotesk } from "next/font/google";
import "./globals.css";
import { ShellFrame } from "@/src/components/shell/ShellFrame";

// BMW Type Next ist proprietär, Hanken Grotesk ist die freie, ähnlich geometrische Alternative.
const hanken = Hanken_Grotesk({
  variable: "--font-hanken",
  subsets: ["latin"],
  weight: ["200", "300", "400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "ReSpec",
  description: "Respect the voice. Define the spec. Evidence-backed product requirements for PM decisions.",
  openGraph: {
    title: "ReSpec",
    description: "Respect the voice. Define the spec.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${hanken.variable} antialiased`} suppressHydrationWarning>
      <body className="min-h-screen" suppressHydrationWarning>
        <ShellFrame>{children}</ShellFrame>
      </body>
    </html>
  );
}
