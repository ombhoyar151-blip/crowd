export default function Topbar({ cameraId, wsStatus }) {
  const statusColor =
    wsStatus === "open"
      ? "var(--success)"
      : wsStatus === "connecting"
      ? "var(--warning)"
      : "var(--critical)";

  const statusLabel =
    wsStatus === "open" ? "Connected" : wsStatus === "connecting" ? "Connecting..." : "Disconnected";

  return (
    <header
      style={{
        height: 56,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 1.5rem",
        borderBottom: "1px solid var(--border-color)",
        background: "var(--bg-surface)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <h2 style={{ fontSize: "1rem", fontWeight: 600 }}>
          {cameraId || "Select a camera"}
        </h2>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span
          style={{
            width: 8,
            height: 8,
            borderRadius: "50%",
            background: statusColor,
            display: "inline-block",
          }}
        />
        <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
          {statusLabel}
        </span>
      </div>
    </header>
  );
}
