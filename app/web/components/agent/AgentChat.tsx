"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState, type FormEvent } from "react";
import styles from "./AgentChat.module.css";

type Receipt = {
  audit: string; memory_head: string; ledger_head: string; event_count: number;
  report_sha256: string; as_of: string; checked_at: string; model?: string;
  conversation_report_ids?: number[];
  files: { path: string; revision: string; digest: string; content: string }[];
};
type Turn = {
  id: number; request_id: string; channel: string; message: string; at: string;
  reply: string | null; state: string; latency_ms: number | null; receipt: Receipt | null;
};
type Status = { memory: Receipt; history: Turn[]; report_count: number };

export function AgentChat() {
  const [status, setStatus] = useState<Status | null>(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const end = useRef<HTMLDivElement>(null);
  const inFlight = useRef(false);

  const refresh = useCallback(async () => {
    const response = await fetch("/api/agent", { cache: "no-store" });
    const value = await response.json();
    if (!response.ok) throw new Error(value.error ?? "Could not read memory");
    setStatus(value as Status);
    setLoading(false);
  }, []);

  useEffect(() => {
    void refresh().catch(e => { setError(String(e.message)); setLoading(false); });
    const timer = setInterval(() => {
      if (!inFlight.current && document.visibilityState === "visible") {
        void refresh().catch(() => {});
      }
    }, 10000);
    return () => clearInterval(timer);
  }, [refresh]);

  useEffect(() => {
    const messages = end.current?.parentElement;
    if (messages) messages.scrollTop = messages.scrollHeight;
  }, [status?.history.length, busy]);

  async function send(text: string, requestId = `web:${crypto.randomUUID()}`) {
    if (inFlight.current) return;
    inFlight.current = true;
    setBusy(true); setError("");
    try {
      const response = await fetch("/api/agent", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, request_id: requestId }),
      });
      const value = await response.json();
      if (!response.ok) throw new Error(value.error ?? "Could not answer");
      setMessage("");
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not answer");
      await refresh().catch(() => {});
    } finally { inFlight.current = false; setBusy(false); }
  }

  function submit(event: FormEvent) { event.preventDefault(); if (message.trim()) void send(message); }

  return <div className={styles.layout}>
    <section className={styles.chat} aria-label="Conversation with Serene">
      <div className={styles.messages} aria-busy={busy || loading}>
        {loading ? <p>Checking memory…</p> : null}
        {!loading && status?.history.length === 0 ? <div className={styles.empty}>
          <p>Ask a question or share an update.</p>
          <button className="button" disabled={busy} onClick={() => void send("What have you learned about Maya's daycare pickups, and what is still uncertain?")}>What has Serene learned?</button>
        </div> : null}
        {status?.history.map(turn => <article className={styles.turn} key={turn.id}>
          <header>You <time dateTime={turn.at}>{new Date(turn.at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</time></header>
          <p className={styles.user}>{turn.message}</p>
          {turn.reply ? <><h3>Serene</h3>
            <p className={styles.answer}>{turn.reply}</p></> :
            <p>{turn.state === "pending" ? "Answer pending." : "No answer was completed."}
              {turn.channel === "web" ? <button className="button" disabled={busy} onClick={() => void send(turn.message, turn.request_id)}>Retry</button> : null}</p>}
        </article>)}
        <div ref={end} />
      </div>
      {busy && <p role="status" className={styles.progress}>Serene is answering…</p>}
      {error ? <p role="alert" className={styles.error}>{error} <button className="button" onClick={() => void refresh().then(() => setError("")).catch(e => setError(e.message))}>Reconnect</button></p> : null}
      <form onSubmit={submit} className={styles.composer}>
        <label htmlFor="agent-message" className="visually-hidden">Message Serene</label>
        <textarea id="agent-message" rows={2} maxLength={4000} value={message} disabled={busy}
          placeholder="Ask Serene…" onChange={event => setMessage(event.target.value)} />
        <button className="button" type="submit" disabled={busy || !message.trim() || !status}>{busy ? "Answering…" : "Send message"}</button>
      </form>
    </section>
    <footer className={styles.memory} aria-label="Shared memory status">
      <span>{status ? "Memory connected · Saved on this computer" : "Connecting…"}</span>
      <Link href="/memory">Open memory</Link>
    </footer>
  </div>;
}
