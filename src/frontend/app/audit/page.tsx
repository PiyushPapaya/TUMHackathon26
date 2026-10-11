import { AuditPageClient } from "@/src/components/AuditPageClient";
import { Suspense } from "react";

export const instant = false;

export default function AuditPage() {
  return <Suspense fallback={<main className="px-6 py-10">Loading decision history...</main>}><AuditPageClient /></Suspense>;
}
