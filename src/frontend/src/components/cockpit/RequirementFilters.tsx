"use client";

import { useState } from "react";
import type { Requirement } from "@/src/lib/api";
import { categoryLabel } from "../badges";
import { RequirementsTable } from "./RequirementsTable";

export function RequirementFilters(props: {
  requirements: Requirement[];
  previousRanks: Record<string, number>;
  highlightRanks: boolean;
  conflictTitles: (r: Requirement) => string[];
  scenarioId: string;
}) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [status, setStatus] = useState("");
  const [level, setLevel] = useState("");
  const [effort, setEffort] = useState("");
  const [order, setOrder] = useState("rank");
  const [conflicts, setConflicts] = useState(false);
  const filtered = props.requirements.filter(r =>
    `${r.title} ${r.description} ${r.id}`.toLowerCase().includes(query.toLowerCase().trim())
    && (!category || r.category === category) && (!status || r.status === status)
    && (!level || r.evidence_level === level) && (!effort || r.effort === effort)
    && (!conflicts || props.conflictTitles(r).length > 0 || Boolean(r.segment_conflicts?.length)))
    .sort((a, b) => order === "title" ? a.title.localeCompare(b.title) : order === "effort" ? ["S", "M", "L"].indexOf(a.effort) - ["S", "M", "L"].indexOf(b.effort) || a.rank - b.rank : a.rank - b.rank);
  const active = query || category || status || level || effort || conflicts;
  function clear() { setQuery(""); setCategory(""); setStatus(""); setLevel(""); setEffort(""); setConflicts(false); setOrder("rank"); }
  return <>
    <div className="mb-4 grid gap-3 sm:grid-cols-3 lg:grid-cols-6">
      <label className="field-label sm:col-span-3 lg:col-span-2">Search requirements<input className="field-control" type="search" placeholder="Title, topic or ID" value={query} onChange={e => setQuery(e.target.value)} /></label>
      <label className="field-label">Topic<select className="field-control" value={category} onChange={e => setCategory(e.target.value)}><option value="">All topics</option>{[...new Set(props.requirements.map(r => r.category))].map(c => <option key={c} value={c}>{categoryLabel(c)}</option>)}</select></label>
      <label className="field-label">Decision<select className="field-control" value={status} onChange={e => setStatus(e.target.value)}><option value="">All decisions</option>{["proposed", "challenged", "approved", "rejected"].map(s => <option key={s} value={s}>{s[0].toUpperCase() + s.slice(1)}</option>)}</select></label>
      <label className="field-label">Evidence<select className="field-control" value={level} onChange={e => setLevel(e.target.value)}><option value="">All evidence</option>{["A - Strong", "B - Moderate", "C - Weak", "D - Assumption"].map(l => <option key={l} value={l[0]}>{l}</option>)}</select></label>
      <label className="field-label">Engineering effort<select className="field-control" value={effort} onChange={e => setEffort(e.target.value)}><option value="">All effort</option><option value="S">Small</option><option value="M">Medium</option><option value="L">Large</option></select></label>
    </div>
    <div className="mb-4 flex flex-wrap items-center justify-between gap-3 text-sm">
      <p role="status" className="text-[var(--grey-500)]">{filtered.length} of {props.requirements.length} requirements</p>
      <div className="flex flex-wrap items-center gap-4">
        <label className="flex min-h-11 items-center gap-2"><input type="checkbox" checked={conflicts} onChange={e => setConflicts(e.target.checked)} />Conflicting evidence</label>
        <select aria-label="Sort requirements" className="field-control !w-auto" value={order} onChange={e => setOrder(e.target.value)}><option value="rank">Priority first</option><option value="effort">Lowest effort first</option><option value="title">Title A-Z</option></select>
        <button type="button" disabled={!active && order === "rank"} onClick={clear} className="min-h-11 text-[var(--blue)] disabled:opacity-40">Clear filters</button>
      </div>
    </div>
    {filtered.length ? <RequirementsTable {...props} requirements={filtered} /> : <p className="border-y border-[var(--hairline)] py-10 text-sm">No requirements match these filters.</p>}
  </>;
}
