export default function AlertBadge({ severity }) {
  const isCritical = severity === "critical";
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 4,
        padding: "2px 10px",
        borderRadius: 999,
        fontSize: "0.7rem",
        fontWeight: 600,
        textTransform: "uppercase",
        letterSpacing: "0.05em",
        background: isCritical
          ? "rgba(239,68,68,0.15)"
          : "rgba(245,158,11,0.15)",
        color: isCritical ? "var(--critical)" : "var(--warning)",
      }}
    >
      <span
        style={{
          width: 5,
          height: 5,
          borderRadius: "50%",
          background: isCritical ? "var(--critical)" : "var(--warning)",
        }}
      />
      {severity}
    </span>
  );
}
