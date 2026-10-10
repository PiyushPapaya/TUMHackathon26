import type { Scenario } from "@/src/lib/api";

export const DEFAULT_SCENARIO_ID = "G60-US";

export function scenarioLabel(scenario: Scenario) {
  return `${scenario.model_name} ${scenario.market}`;
}
