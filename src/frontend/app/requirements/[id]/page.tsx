import { RequirementDetailPageClient } from "@/src/components/RequirementDetailPageClient";
import { Suspense } from "react";

export const instant = false;

export default async function RequirementDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <Suspense fallback={<main className="px-6 py-10">Loading requirement...</main>}><RequirementDetailPageClient id={id} /></Suspense>;
}
