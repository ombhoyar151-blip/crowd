import { useEffect, useRef, useState } from "react";

export default function StatCard({ label, value, unit, color }) {
  const [displayValue, setDisplayValue] = useState(value);
  const rafRef = useRef(null);
  const prevRef = useRef(value);

  useEffect(() => {
    const start = prevRef.current;
    const diff = value - start;
    if (diff === 0) return;
    const duration = 300;
    const startTime = performance.now();

    const animate = (now) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayValue(Math.round(start + diff * eased));
      if (progress < 1) {
        rafRef.current = requestAnimationFrame(animate);
      }
    };

    rafRef.current = requestAnimationFrame(animate);
    prevRef.current = value;
    return () => cancelAnimationFrame(rafRef.current);
  }, [value]);

  return (
    <div
      style={{
        background: "var(--bg-surface)",
        border: "1px solid var(--border-color)",
        borderRadius: "var(--radius)",
        padding: "1rem 1.25rem",
        backdropFilter: "blur(12px)",
      }}
    >
      <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: 4, fontWeight: 500 }}>
        {label}
      </div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 4 }}>
        <span
          style={{
            fontSize: "1.75rem",
            fontWeight: 700,
            fontFamily: "var(--font-mono)",
            color: color || "var(--text-primary)",
            lineHeight: 1,
          }}
        >
          {displayValue}
        </span>
        {unit && (
          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
            {unit}
          </span>
        )}
      </div>
    </div>
  );
}
