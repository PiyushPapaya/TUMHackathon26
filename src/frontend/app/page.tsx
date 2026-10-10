import { readdir } from "node:fs/promises";
import path from "node:path";
import { HomePage } from "@/src/components/home/HomePage";

// Listet vorhandene Bilder in public/media (z. B. /media/poster.jpg), damit fehlende Medien keinen 404 auslösen.
async function listMedia(dir = ""): Promise<string[]> {
  const root = path.join(process.cwd(), "public", "media", dir);
  try {
    const entries = await readdir(root, { withFileTypes: true });
    const nested = await Promise.all(
      entries.map(async (e) =>
        e.isDirectory() ? (e.name === "car" ? [] : listMedia(path.join(dir, e.name))) : [`/media/${path.posix.join(dir.replaceAll("\\", "/"), e.name)}`],
      ),
    );
    return nested.flat();
  } catch {
    return [];
  }
}

// "use cache": Dateisystem-Zugriff ist bei cacheComponents nur erlaubt, wenn das Ergebnis beim Build zwischengespeichert wird.
async function getMedia() {
  "use cache";
  return listMedia();
}

// Cinematic-Startseite. Das Cockpit selbst liegt unter /cockpit.
export default async function Home() {
  return <HomePage media={await getMedia()} />;
}
