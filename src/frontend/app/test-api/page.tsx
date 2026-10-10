"use client";

import { useEffect, useState } from "react";
import { getRequirements, type Requirement } from "@/src/lib/api";

/**
 * Nur zum Prüfen von Ticket D1 (API-Schicht): zeigt die Anforderungen des
 * Beispiel-Bundles roh an. Die echte Startseite kommt in Ticket D2.
 */
export default function TestApiPage() {
  const [requirements, setRequirements] = useState<Requirement[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getRequirements("G60-US")
      .then(setRequirements)
      .catch((err: Error) => setError(err.message));
  }, []);

  if (error) {
    return <p className="p-8 text-red-600">{error}</p>;
  }

  if (!requirements) {
    return <p className="p-8">Loading…</p>;
  }

  return (
    <ul className="p-8">
      {requirements.map((req) => (
        <li key={req.id}>
          #{req.rank} {req.title} ({req.score})
        </li>
      ))}
    </ul>
  );
}
