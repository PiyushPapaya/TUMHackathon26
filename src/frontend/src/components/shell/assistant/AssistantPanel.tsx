"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Icon } from "@/src/components/ui/Icon";
import { Logo } from "@/src/components/ui/Logo";
import { EvidenceDot } from "@/src/components/badges";
import { GuideTab } from "./GuideTab";
import type { Message, Tab } from "./AssistantProvider";

const QUICK = ["What should we build first?", "Show the ranked list", "What does red mean?", "Families and charging", "Where is the audit trail?", "Compare markets"];

function Bubble({ m }: { m: Message }) {
  if (m.role === "user") {
    return <p className="ml-10 self-end bg-[var(--blue)] px-4 py-2.5 text-sm text-white">{m.text}</p>;
  }
  return (
    <div className="mr-6 grid gap-3 self-start">
      <p className="bg-[var(--grey-100)] px-4 py-3 text-sm leading-relaxed text-[var(--ink)]">{m.text}</p>
      {m.hits && m.hits.length > 0 && (
        <ol className="grid gap-px bg-[var(--hairline)]">
          {m.hits.map((h) => (
            <li key={`${h.scenarioId}-${h.id}`} className="bg-white">
              <Link href={`/requirements/${h.id}`} className="group flex gap-3 px-4 py-3 hover:bg-[var(--grey-100)]">
                <span className="mt-1.5"><EvidenceDot level={h.level} /></span>
                <span className="flex-1">
                  <span className="block text-sm text-[var(--ink)] group-hover:text-[var(--blue)]">{h.title}</span>
                  <span className="mt-0.5 block text-[11px] text-[var(--grey-500)]">{h.scenarioId}{h.note ? ` · ${h.note}` : ""}</span>
                </span>
                <Icon name="chevron" size={14} className="mt-1 text-[var(--grey-500)]" />
              </Link>
            </li>
          ))}
        </ol>
      )}
      {m.links?.map((l) => (
        <Link key={l.href} href={l.href} className="inline-flex items-center gap-1 text-sm font-semibold text-[var(--blue)] hover:text-[var(--blue-hover)]">
          {l.label} <Icon name="arrow" size={14} />
        </Link>
      ))}
      {m.source && <p className="text-[10px] uppercase tracking-[0.12em] text-[var(--grey-500)]">{m.source}</p>}
    </div>
  );
}

// Seitenleiste mit zwei Tabs. Chat: Schnellfragen + Eingabe; Guide: die fünf Schritte kompakt.
export function AssistantPanel({
  isOpen, tab, onTab, onToggle, messages, busy, onSend,
}: {
  isOpen: boolean; tab: Tab; onTab: (t: Tab) => void; onToggle: () => void;
  messages: Message[]; busy: boolean; onSend: (text: string) => void;
}) {
  const [text, setText] = useState("");
  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, busy]);
  useEffect(() => {
    if (isOpen && tab === "chat") inputRef.current?.focus();
  }, [isOpen, tab]);

  return (
    <>
      {/* Offen: Der Knopf verschwindet, damit er das Eingabefeld nicht verdeckt. Schließen über das X im Kopf. */}
      {!isOpen && <button
        type="button"
        aria-label="Open assistant"
        aria-expanded={false}
        onClick={onToggle}
        className="group fixed bottom-6 right-6 z-[60] flex h-14 items-center bg-[var(--blue)] text-white shadow-[0_8px_30px_rgba(28,105,212,0.35)] transition-colors hover:bg-[var(--blue-hover)]"
      >
        <span className="absolute inset-0 animate-ping bg-[var(--blue)] opacity-20 [animation-iteration-count:3]" aria-hidden="true" />
        <span className="flex h-14 w-14 items-center justify-center"><Icon name="chat" /></span>
        <span className="max-w-0 overflow-hidden whitespace-nowrap text-sm font-semibold transition-[max-width,padding] duration-300 group-hover:max-w-40 group-hover:pr-5">
          Ask Signal2Spec
        </span>
      </button>}

      <aside
        aria-label="Signal2Spec assistant"
        aria-hidden={!isOpen}
        className={`fixed bottom-0 right-0 top-0 z-50 flex w-full max-w-[420px] flex-col border-l border-[var(--hairline)] bg-white shadow-[-20px_0_60px_rgba(0,0,0,0.12)] transition-transform duration-300 ease-out ${
          isOpen ? "translate-x-0" : "pointer-events-none translate-x-full"
        }`}
      >
        <header className="bg-[var(--black)] px-6 pb-0 pt-6 text-white">
          <div className="flex items-center justify-between">
            <Logo light size={28} />
            <button type="button" onClick={onToggle} aria-label="Close assistant" className="flex h-10 w-10 items-center justify-center text-white/70 hover:text-white">
              <Icon name="close" />
            </button>
          </div>
          <nav className="mt-6 flex gap-6" aria-label="Assistant tabs">
            {(["chat", "guide"] as const).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => onTab(t)}
                className={`border-b-2 pb-3 text-sm font-semibold capitalize ${tab === t ? "border-[var(--m-light)] text-white" : "border-transparent text-white/50 hover:text-white"}`}
              >
                {t}
              </button>
            ))}
          </nav>
        </header>

        {tab === "guide" ? (
          <GuideTab />
        ) : (
          <>
            <div ref={listRef} className="flex flex-1 flex-col gap-4 overflow-y-auto px-6 py-6">
              {messages.map((m, i) => <Bubble key={i} m={m} />)}
              {busy && <p className="self-start bg-[var(--grey-100)] px-4 py-3 text-sm text-[var(--grey-500)]">Reading your question and ranking the data… (a few seconds the first time)</p>}
              {messages.length <= 1 && (
                <div className="flex flex-wrap gap-2">
                  {QUICK.map((q) => (
                    <button key={q} type="button" onClick={() => onSend(q)} className="border border-[var(--hairline)] px-3 py-1.5 text-xs text-[var(--ink)] hover:border-[var(--ink)]">
                      {q}
                    </button>
                  ))}
                </div>
              )}
            </div>
            <form
              className="flex border-t border-[var(--hairline)]"
              onSubmit={(e) => {
                e.preventDefault();
                onSend(text);
                setText("");
              }}
            >
              <input
                ref={inputRef}
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Ask about the data or where to go…"
                aria-label="Message to the assistant"
                className="h-14 flex-1 px-5 text-sm focus:outline-none"
              />
              <button type="submit" disabled={busy || !text.trim()} aria-label="Send" className="flex w-14 items-center justify-center text-[var(--blue)] disabled:text-[var(--grey-500)]">
                <Icon name="arrow" />
              </button>
            </form>
            {messages.length > 1 && (
              <div className="flex gap-2 overflow-x-auto border-t border-[var(--hairline)] px-4 py-2">
                {QUICK.slice(0, 4).map((q) => (
                  <button key={q} type="button" onClick={() => onSend(q)} className="shrink-0 px-2 py-1 text-[11px] text-[var(--grey-500)] hover:text-[var(--ink)]">
                    {q}
                  </button>
                ))}
              </div>
            )}
            <p className="px-6 pb-3 pt-1 text-[10px] text-[var(--grey-500)]">Answers cite only requirements that exist in the data.</p>
          </>
        )}
      </aside>
    </>
  );
}
