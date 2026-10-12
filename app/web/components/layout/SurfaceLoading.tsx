import styles from "./SurfaceLoading.module.css";

// Shared route and record loading, with decorative skeletons and one spoken
// status. No invented percentages or minimum wait before content can appear.
export function SurfaceLoading({ label = "Loading Serene", compact = false }: { label?: string; compact?: boolean }) {
  return (
    <div className={styles.loading} data-compact={compact || undefined} role="status" aria-live="polite" aria-label={label}>
      <div className={styles.intro}>
        <svg className={styles.bloom} viewBox="0 0 80 80" aria-hidden="true" focusable="false">
          {[0, 72, 144, 216, 288].map((angle) => (
            <ellipse key={angle} cx="40" cy="25" rx="12" ry="20" transform={`rotate(${angle} 40 40)`} />
          ))}
          <circle cx="40" cy="40" r="6" />
        </svg>
        <div>
          <p className={styles.label}>{label}</p>
          <p className={styles.hint}>A moment to bring everything into view.</p>
        </div>
      </div>
      <div className={styles.skeleton} aria-hidden="true">
        {!compact && <div className={styles.heading}><span /><span /></div>}
        <div className={styles.columns}>
          <div className={styles.sheet}>
            <span className={styles.short} /><span className={styles.title} />
            <div className={styles.feature} />
            <span /><span /><span className={styles.short} />
          </div>
          <div className={styles.side}>
            <div className={styles.sheet}><span className={styles.short} /><span /><span /></div>
            <div className={styles.sheet}><span className={styles.short} /><span /><span /></div>
          </div>
        </div>
      </div>
    </div>
  );
}
