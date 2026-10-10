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
  title: "Signal2Spec",
  description: "From customer voice to the next BMW. Evidence-backed product requirements for PM decisions.",
  openGraph: {
    title: "Signal2Spec",
    description: "From customer voice to the next BMW.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${hanken.variable} antialiased`}>
      <body className="min-h-screen" suppressHydrationWarning>
        <ShellFrame>{children}</ShellFrame>
      </body>
    </html>
  );
}
