// Ländercode (GB, FR …) -> lesbarer Name. Intl statt eigener Liste, weil neue Märkte (KR, JP, CA) dann ohne Pflege funktionieren.
const NAMES = new Intl.DisplayNames(["en"], { type: "region" });

export function countryName(code: string): string {
  try {
    return NAMES.of(code) ?? code;
  } catch {
    return code; // ungültiger Code: lieber roh anzeigen als abstürzen
  }
}
