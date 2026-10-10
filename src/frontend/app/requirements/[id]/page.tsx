/**
 * Ticket D3: Route-Wrapper für /requirements/[id]. Bleibt Server-Komponente, weil nur dort
 * `export const instant = false` erlaubt ist (Next 16 Cache Components): echte Anforderungs-IDs
 * kommen aus der Pipeline und sind beim Build nicht bekannt, die Daten holt ohnehin der Client
 * per fetch, also gibt es hier nichts statisch vorzurendern. Die eigentliche Seite ist eine
 * Client-Komponente (src/components/RequirementDetailPageClient.tsx), weil D4 hier das
 * Entscheidungs-Panel mit State + Re-Fetch ergänzt.
 */
import { RequirementDetailPageClient } from "@/src/components/RequirementDetailPageClient";

export const instant = false;

export default async function RequirementDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <RequirementDetailPageClient id={id} />;
}
