import { formatDistanceToNow } from "date-fns";
import AlertBadge from "./AlertBadge";

export default function AlertItem({ alert, onResolve }) {
  const isResolved = !!alert.resolved_at;

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "10px 12px",
        borderRadius: 8,
        background: isResolved ? "transparent" : "rgba(255,255,255,0.02)",
        border: "1px solid var(--border-color)",
        opacity: isResolved ? 0.6 : 1,
      }}
    >
      <AlertBadge severity={alert.severity} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            fontSize: "0.8125rem",
            fontWeight: 500,
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          {alert.zone_name}
        </div>
        <div
          style={{
            fontSize: "0.75rem",
            color: "var(--text-muted)",
            marginTop: 2,
          }}
        >
          {alert.count}/{alert.threshold} \u00B7{" "}
          {formatDistanceToNow(new Date(alert.time), { addSuffix: true })}
        </div>
      </div>
      {!isResolved && (
        <button
          onClick={() => onResolve?.(alert.id)}
          style={{
            padding: "4px 12px",
            borderRadius: 6,
            border: "1px solid var(--border-color)",
            background: "transparent",
            color: "var(--text-muted)",
            fontSize: "0.75rem",
            cursor: "pointer",
            transition: "var(--transition)",
            whiteSpace: "nowrap",
          }}
          onMouseEnter={(e) => (e.target.style.color = "var(--accent)")}
          onMouseLeave={(e) => (e.target.style.color = "var(--text-muted)")}
        >
          Resolve
        </button>
      )}
      {isResolved && (
        <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
          Resolved
        </span>
      )}
    </div>
  );
}
