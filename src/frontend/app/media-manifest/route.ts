import { readFile } from "node:fs/promises";
import path from "node:path";

// Liefert das Frame-Manifest der Auto-Szene oder {available:false}.
// Warum eine Route statt direktem fetch auf die Datei: fehlt das Video-Material noch, würde der Browser
// einen 404 in die Konsole schreiben. So bleibt die Konsole sauber und die Fallback-Szene greift still.
export async function GET() {
  try {
    const file = path.join(process.cwd(), "public", "media", "car", "manifest.json");
    const manifest = JSON.parse(await readFile(file, "utf8"));
    return Response.json({ available: true, ...manifest });
  } catch {
    return Response.json({ available: false });
  }
}
