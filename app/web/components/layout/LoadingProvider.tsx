"use client";

import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode, type Ref } from "react";
import { BloomMark } from "@/components/brand/BloomMark";
import styles from "./SurfaceLoading.module.css";

type Register = (label: string) => () => void;
const LoadingContext = createContext<Register | null>(null);

/** Persists across Suspense boundaries so the logo can return to the header
 * when the record is ready and its loading component has unmounted. */
export function LoadingProvider({ children, initialLoading = false }: { children: ReactNode; initialLoading?: boolean }) {
  const [requests, setRequests] = useState(new Map<symbol, string>());
  const register = useCallback<Register>((text) => {
    const id = Symbol();
    setRequests((current) => new Map(current).set(id, text));
    return () => setRequests((current) => {
      const next = new Map(current);
      next.delete(id);
      return next;
    });
  }, []);

  return (
    <LoadingContext.Provider value={register}>
      {children}
      <LoadingLayer requests={requests} initialLoading={initialLoading} />
    </LoadingContext.Provider>
  );
}

// Initial hydration and animation updates belong to the overlay alone. They
// must not re-render the server-rendered route while it is still hydrating.
function LoadingLayer({ requests, initialLoading }: { requests: ReadonlyMap<symbol, string>; initialLoading: boolean }) {
  const [booting, setBooting] = useState(initialLoading);
  const [visible, setVisible] = useState(initialLoading);
  const [returning, setReturning] = useState(false);
  const logo = useRef<HTMLDivElement>(null);
  const pending = booting || requests.size > 0;
  const label = [...requests.values()].at(-1) ?? "Loading Serene";

  useEffect(() => setBooting(false), []);

  useEffect(() => {
    if (pending) {
      setVisible(true);
      setReturning(false);
      return;
    }
    if (!visible) return;

    const element = logo.current;
    const target = document.querySelector<HTMLElement>("[data-shell-bar] > a [data-brand-mark]");
    if (!element || !target || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setVisible(false);
      return;
    }

    const from = element.getBoundingClientRect();
    const to = target.getBoundingClientRect();
    const dx = to.x + to.width / 2 - from.x - from.width / 2;
    const dy = to.y + to.height / 2 - from.y - from.height / 2;
    const scale = to.width / from.width;
    const spin = element.firstElementChild as HTMLElement;
    const rotation = getComputedStyle(spin).transform;
    setReturning(true);
    const settle = spin.animate([{ transform: rotation }, { transform: "rotate(0deg)" }],
      { duration: 420, easing: "cubic-bezier(0.22, 1, 0.36, 1)", fill: "forwards" });
    const flight = element.animate([
      { transform: "translate(-50%, -50%) scale(1)" },
      { transform: `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px)) scale(${scale})` },
    ], { duration: 420, easing: "cubic-bezier(0.22, 1, 0.36, 1)", fill: "forwards" });
    let cancelled = false;
    flight.finished.then(() => {
      if (!cancelled) setVisible(false);
    }).catch(() => {
      if (!cancelled) setVisible(false);
    });
    return () => {
      cancelled = true;
      flight.cancel();
      settle.cancel();
    };
  }, [pending, visible]);

  return visible ? <LoadingOverlay label={label} returning={returning} logoRef={logo} /> : null;
}

function LoadingOverlay({ label, returning = false, logoRef }: {
  label: string;
  returning?: boolean;
  logoRef?: Ref<HTMLDivElement>;
}) {
  return (
    <div className={styles.overlay} data-page-loader data-state={returning ? "returning" : "loading"}
      role="status" aria-live="polite" aria-label={label}>
      <div className={styles.backdrop} />
      <div ref={logoRef} className={styles.logo} data-loading-logo aria-hidden="true">
        <div className={styles.spin}><BloomMark className={styles.mark} /></div>
      </div>
      <p className={styles.label}>{label}</p>
    </div>
  );
}

/** Registers actual work; no timer or invented progress delays the content. */
export function SurfaceLoading({ label = "Loading Serene", compact: _compact = false }: { label?: string; compact?: boolean }) {
  const register = useContext(LoadingContext);
  useEffect(() => register?.(label), [register, label]);
  return register ? null : <LoadingOverlay label={label} />;
}
