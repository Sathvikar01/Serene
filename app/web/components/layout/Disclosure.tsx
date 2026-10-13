import type { ReactNode } from "react";
import styles from "./Disclosure.module.css";

/** Keep the summary readable; the complete record remains one click away. */
export function Disclosure({ title, children, open = false }: { title: string; children: ReactNode; open?: boolean }) {
  return <details className={styles.details} open={open || undefined} data-record-details>
    <summary>{title}</summary>
    <div className={styles.body}>{children}</div>
  </details>;
}
