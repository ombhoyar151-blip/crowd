import { useContext } from "react";
import { CameraContext } from "../../context/CameraContext";
import { useAuth } from "../../hooks/useAuth";
import { useCameras } from "../../hooks/useCameras";
import GlassCard from "../../components/common/GlassCard";
import Spinner from "../../components/common/Spinner";

export default function SettingsPage() {
  const { user } = useAuth();
  const { cameraId } = useContext(CameraContext);
  const { cameras, loading } = useCameras();

  const cam = cameras.find((c) => c.id === cameraId);

  if (loading) return <Spinner />;

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))",
        gap: 16,
      }}
    >
      <GlassCard>
        <h3
          style={{
            fontSize: "0.8125rem",
            fontWeight: 600,
            marginBottom: 12,
            color: "var(--text-muted)",
            textTransform: "uppercase",
            letterSpacing: "0.05em",
          }}
        >
          Camera Info
        </h3>
        {cam ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <Row label="ID" value={cam.id} />
            <Row label="Name" value={cam.name} />
            <Row label="Source" value={cam.source_type} />
            <Row label="URL" value={cam.source_url || "-"} />
            <Row
              label="Status"
              value={cam.is_active ? "Active" : "Inactive"}
            />
          </div>
        ) : (
          <p style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>
            No camera selected
          </p>
        )}
      </GlassCard>

      <GlassCard>
        <h3
          style={{
            fontSize: "0.8125rem",
            fontWeight: 600,
            marginBottom: 12,
            color: "var(--text-muted)",
            textTransform: "uppercase",
            letterSpacing: "0.05em",
          }}
        >
          User Info
        </h3>
        {user ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <Row label="Username" value={user.username} />
            <Row label="Role" value={user.role} />
            <Row label="Active" value={user.is_active ? "Yes" : "No"} />
          </div>
        ) : (
          <p style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>
            Not authenticated
          </p>
        )}
      </GlassCard>

      <GlassCard>
        <h3
          style={{
            fontSize: "0.8125rem",
            fontWeight: 600,
            marginBottom: 12,
            color: "var(--text-muted)",
            textTransform: "uppercase",
            letterSpacing: "0.05em",
          }}
        >
          Alert Config
        </h3>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <Row label="Cooldown" value="60s" />
          <Row label="Critical Ratio" value="2.0x threshold" />
          <Row label="Email Alerts" value="Disabled" />
          <Row label="Telegram Alerts" value="Disabled" />
        </div>
      </GlassCard>
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        fontSize: "0.8125rem",
        padding: "4px 0",
        borderBottom: "1px solid rgba(255,255,255,0.04)",
      }}
    >
      <span style={{ color: "var(--text-muted)" }}>{label}</span>
      <span style={{ color: "var(--text-primary)", fontWeight: 500 }}>
        {value}
      </span>
    </div>
  );
}
