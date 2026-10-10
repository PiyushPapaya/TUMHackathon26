import { redirect } from "next/navigation";

// Overview ist in die Startseite gewandert (Abschnitt "How it works"), weil beide dasselbe erzählten.
// Die Weiterleitung hält alte Links und Lesezeichen am Leben.
export default function OverviewPage() {
  redirect("/#flow");
}
