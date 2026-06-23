import { useContext, useEffect, useState } from "react";
import { CameraContext } from "../../context/CameraContext";
import { useAuth } from "../../hooks/useAuth";
import { useWebSocket } from "../../hooks/useWebSocket";
import { useSnapshot } from "../../hooks/useSnapshot";
import { useAlerts } from "../../hooks/useAlerts";
import LiveStats from "../../components/LiveStats/LiveStats";
import HeatmapViewer from "../../components/HeatmapViewer/HeatmapViewer";
import ZoneStatusGrid from "../../components/ZoneStatusGrid/ZoneStatusGrid";
import CountChart from "../../components/CountChart/CountChart";
import AlertPanel from "../../components/AlertPanel/AlertPanel";
import CameraSelector from "../../components/CameraSelector/CameraSelector";
import GlassCard from "../../components/common/GlassCard";
import { useCameras } from "../../hooks/useCameras";
import SmallCameraPreview from "../../components/SmallCameraPreview/SmallCameraPreview";

export default function DashboardPage() {
  const { cameraId, selectCamera } = useContext(CameraContext);
  const { token } = useAuth();
  const { cameras } = useCameras();

  const { status, subscribe } = useWebSocket(cameraId, token);
  const { latestSnapshot, countHistory, fps } = useSnapshot(subscribe);
  const { liveAlerts, unresolvedCount, resolve } = useAlerts({ subscribe, cameraId });

  const zones = latestSnapshot?.zone_statuses || [];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <CameraSelector
            cameras={cameras}
            value={cameraId}
            onChange={selectCamera}
          />
          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
            {unresolvedCount > 0 && `${unresolvedCount} unresolved`}
          </span>
        </div>
        <SmallCameraPreview latestSnapshot={latestSnapshot} />
      </div>

      <LiveStats latestSnapshot={latestSnapshot} fps={fps} />

      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 16 }}>
        <HeatmapViewer cameraId={cameraId} />
        <GlassCard>
          <h3
            style={{
              fontSize: "0.8125rem",
              fontWeight: 600,
              marginBottom: 10,
              color: "var(--text-muted)",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
            }}
          >
            Zones
          </h3>
          <ZoneStatusGrid zoneStatuses={zones} />
        </GlassCard>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 16 }}>
        <GlassCard>
          <h3
            style={{
              fontSize: "0.8125rem",
              fontWeight: 600,
              marginBottom: 10,
              color: "var(--text-muted)",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
            }}
          >
            Live Count
          </h3>
          <CountChart data={countHistory} />
        </GlassCard>
        <GlassCard>
          <h3
            style={{
              fontSize: "0.8125rem",
              fontWeight: 600,
              marginBottom: 10,
              color: "var(--text-muted)",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
            }}
          >
            Recent Alerts
          </h3>
          <AlertPanel alerts={liveAlerts} onResolve={resolve} />
        </GlassCard>
      </div>
    </div>
  );
}
