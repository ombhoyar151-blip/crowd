import styles from "./ZoneStatusGrid.module.css";

export default function ZoneCard({ zoneName, count, threshold, isViolated }) {
  const ratio = threshold > 0 ? count / threshold : 0;
  const barWidth = Math.min(ratio, 1) * 100;

  const barColor =
    ratio >= 1
      ? "var(--critical)"
      : ratio >= 0.75
      ? "var(--warning)"
      : "var(--success)";

  return (
    <div className={`${styles.card} ${isViolated ? styles.violated : ""}`}>
      <div className={styles.header}>
        <span className={styles.name}>{zoneName}</span>
        <span className={styles.count} style={{ color: barColor }}>
          {count}
          <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>
            /{threshold}
          </span>
        </span>
      </div>
      <div className={styles.barTrack}>
        <div
          className={styles.barFill}
          style={{ width: `${barWidth}%`, background: barColor }}
        />
      </div>
    </div>
  );
}
