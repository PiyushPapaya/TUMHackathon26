import { Eyebrow, SectionHeading } from "./Typography";

// Einheitlicher Seitenkopf ohne Kasten: kleines Label, helle Überschrift mit Punkt, ein Satz Erklärung.
export function PageHeader({ eyebrow, title, children, action }: { eyebrow: string; title: string; children?: React.ReactNode; action?: React.ReactNode }) {
  return (
    <header className="flex flex-wrap items-end justify-between gap-6 pb-10">
      <div>
        <Eyebrow>{eyebrow}</Eyebrow>
        <SectionHeading as="h1" className="mt-3">{title}</SectionHeading>
        {children && <p className="mt-4 max-w-2xl text-[var(--grey-500)]">{children}</p>}
      </div>
      {action}
    </header>
  );
}

export function ErrorNote({ message }: { message: string }) {
  return (
    <div role="alert" className="mb-6 border border-[var(--m-red)] bg-white px-4 py-3 text-sm text-[var(--m-red)]">
      {message}
    </div>
  );
}

export function Loading({ what }: { what: string }) {
  return <p className="py-8 text-sm text-[var(--grey-500)]">Loading {what}...</p>;
}
