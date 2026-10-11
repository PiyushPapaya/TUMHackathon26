"use client";

import { createContext, useContext, useState } from "react";
import Image from "next/image";

// Liste der Dateien in public/media (vom Server ermittelt). Fehlt eine Datei, rendern wir gar kein <img>,
// sonst schreibt der Browser einen 404 in die Konsole.
export const MediaContext = createContext<string[]>([]);

// Bild, das still verschwindet, wenn die Datei (noch) fehlt. Die echten Flow-Bilder kommen später in public/media/.
// `sizes` = echte Anzeigebreite, damit Next.js keine zu großen Varianten lädt (Standard: volle Breite wie im Hero).
export function MediaImage({ src, alt, priority, className = "", sizes = "100vw" }: { src: string; alt: string; priority?: boolean; className?: string; sizes?: string }) {
  const available = useContext(MediaContext);
  const [failed, setFailed] = useState(false);
  if (failed || !available.includes(src)) return null;
  return (
    <Image
      src={src}
      alt={alt}
      fill
      priority={priority}
      sizes={sizes}
      className={`object-cover ${className}`.trim()}
      suppressHydrationWarning
      onError={() => setFailed(true)}
    />
  );
}
