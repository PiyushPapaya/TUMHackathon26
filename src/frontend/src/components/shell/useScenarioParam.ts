"use client";

import { useSearchParams } from "next/navigation";
import { DEFAULT_SCENARIO_ID } from "./scenarioLabel";

// Das gewählte Szenario steckt in der URL (?scenario=). Jede Seite liest es hier, der Header schreibt es.
// Warum URL statt State: Links aus Mega-Menü und Startseite können direkt auf ein Szenario zeigen.
export function useScenarioParam(): string {
  return useSearchParams().get("scenario") ?? DEFAULT_SCENARIO_ID;
}
