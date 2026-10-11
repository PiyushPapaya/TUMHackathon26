import { redirect } from "next/navigation";

// Overview ist in die Startseite gewandert (letztes Kapitel der Scroll-Story), weil beide dasselbe erzählten.
// Die Weiterleitung hält alte Links und Lesezeichen am Leben.
export default function OverviewPage() {
  redirect("/#how");
}
