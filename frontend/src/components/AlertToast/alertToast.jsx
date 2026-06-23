import { toast } from "react-hot-toast";

export function showAlertToast(alert) {
  const severityColor =
    alert.severity === "critical" ? "var(--critical)" : "var(--warning)";

  toast.custom(
    (t) => (
      <div
        style={{
          background: "rgba(10,14,26,0.95)",
          border: `1px solid ${severityColor}40`,
          borderRadius: 12,
          padding: "12px 16px",
          backdropFilter: "blur(12px)",
          color: "#f1f5f9",
          minWidth: 280,
          boxShadow: `0 4px 20px ${severityColor}20`,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
          <span style={{ fontSize: "1.25rem" }}>
            {alert.severity === "critical" ? "\uD83D\uDEA8" : "\u26A0\uFE0F"}
          </span>
          <span
            style={{
              fontSize: "0.75rem",
              fontWeight: 600,
              color: severityColor,
              textTransform: "uppercase",
            }}
          >
            {alert.severity} Alert
          </span>
        </div>
        <div style={{ fontSize: "0.875rem", marginBottom: 2 }}>
          {alert.zone_name}: {alert.count}/{alert.threshold}
        </div>
        <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
          {alert.camera_id}
        </div>
        <div
          style={{
            marginTop: 8,
            height: 2,
            borderRadius: 1,
            background: severityColor,
            animation: "shrink 8s linear forwards",
          }}
        />
        <style>{`@keyframes shrink { from { width: 100%; } to { width: 0%; } }`}</style>
      </div>
    ),
    { duration: 8000, position: "top-right" }
  );
}
