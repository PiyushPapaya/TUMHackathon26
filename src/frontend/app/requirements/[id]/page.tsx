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
