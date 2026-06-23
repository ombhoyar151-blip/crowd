export default function Badge({ variant = "default", children }) {
  const colors = {
    default: { bg: "rgba(255,255,255,0.08)", color: "var(--text-muted)" },
    active: { bg: "rgba(16,185,129,0.15)", color: "var(--success)" },
    warning: { bg: "rgba(245,158,11,0.15)", color: "var(--warning)" },
    critical: { bg: "rgba(239,68,68,0.15)", color: "var(--critical)" },
    info: { bg: "rgba(99,102,241,0.15)", color: "var(--accent)" },
  };
  const s = colors[variant] || colors.default;

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 4,
        padding: "2px 10px",
        borderRadius: 999,
        fontSize: "0.75rem",
        fontWeight: 600,
        background: s.bg,
        color: s.color,
        textTransform: "uppercase",
        letterSpacing: "0.05em",
      }}
    >
      {children}
    </span>
  );
}
