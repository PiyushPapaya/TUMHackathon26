"use client";

import { useEffect, useState } from "react";
import {
  getAudit,
  getAuditTimeline,
  type AuditEvent,
  type AuditTimelineEvent,
} from "@/src/lib/api";

const ACTOR_LABEL: Record<string, string> = {
  ai: "AI",
  human: "Human",
  system: "System",
};

function formatTime(value: string) {
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function payloadPreview(payload: Record<string, unknown>) {
  const text = JSON.stringify(payload, null, 2);
  return text.length > 2200 ? `${text.slice(0, 2200)}\n...` : text;
}

export function AuditTrail({
  scenarioId,
  requirementId,
  compact = false,
}: {
  scenarioId?: string;
  requirementId?: string;
  compact?: boolean;
}) {
  const [timeline, setTimeline] = useState<AuditTimelineEvent[]>([]);
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const filter = { scenarioId, requirementId };
    Promise.all([getAuditTimeline(filter), getAudit(filter)])
      .then(([nextTimeline, nextEvents]) => {
        if (cancelled) return;
        setTimeline(nextTimeline);
        setEvents(nextEvents);
        setError(null);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [requirementId, scenarioId]);

  const bySeq = new Map(events.map((event) => [event.seq, event]));

  if (loading) {
    return <p className="rounded-sm border border-zinc-200 dark:border-zinc-800 bg-surface p-4 text-sm text-zinc-500 dark:text-zinc-400">Loading audit trail...</p>;
  }

  if (error) {
    return (
      <div className="rounded-sm border border-rose-300 bg-rose-50 p-4 text-sm text-rose-800 dark:border-rose-800 dark:bg-rose-950 dark:text-rose-300">
        {error}
      </div>
    );
  }

  if (timeline.length === 0) {
    return (
      <div className="rounded-sm border border-zinc-200 dark:border-zinc-800 bg-surface p-4 text-sm text-zinc-500 dark:text-zinc-400">
        No audit events for this selection yet.
      </div>
    );
  }

  return (
    <div className={compact ? "space-y-3" : "space-y-4"}>
      {timeline.map((item) => {
        const event = bySeq.get(item.seq);
        return (
          <article
            key={item.seq}
            className="rounded-lg border border-zinc-200 dark:border-zinc-800 bg-surface p-4"
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-foreground">{item.sentence}</p>
                <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
                  #{item.seq} · {formatTime(item.ts)} · {ACTOR_LABEL[item.actor.type] ?? item.actor.type}:{" "}
                  {item.actor.name}
                </p>
              </div>
              <span className="rounded-full border border-zinc-300 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-900 px-3 py-1 text-xs font-semibold text-zinc-700 dark:text-zinc-300">
                {item.event_type}
              </span>
            </div>
            {item.rationale && <p className="mt-3 text-sm text-zinc-700 dark:text-zinc-300">{item.rationale}</p>}
            {event && Object.keys(event.payload ?? {}).length > 0 && (
              <details className="mt-3 rounded-sm border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 p-3">
                <summary className="cursor-pointer text-xs font-semibold uppercase tracking-wide text-zinc-600 dark:text-zinc-400">
                  Before / after payload
                </summary>
                <pre className="mt-2 overflow-auto text-xs leading-relaxed text-zinc-700 dark:text-zinc-300">
                  {payloadPreview(event.payload)}
                </pre>
              </details>
            )}
          </article>
        );
      })}
    </div>
  );
}
