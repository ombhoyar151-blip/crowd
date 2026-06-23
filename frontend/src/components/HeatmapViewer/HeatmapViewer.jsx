import { useHeatmap } from "../../hooks/useHeatmap";

export default function HeatmapViewer({ cameraId }) {
  const { heatmapUrl, lastUpdated } = useHeatmap(cameraId);

  if (!heatmapUrl) {
    return (
      <div
        style={{
          aspectRatio: "16/9",
          background: "var(--bg-surface)",
          borderRadius: "var(--radius)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "var(--text-muted)",
          fontSize: "0.875rem",
          border: "1px solid var(--border-color)",
        }}
      >
        Waiting for heatmap...
      </div>
    );
  }

  return (
    <div
      style={{
        position: "relative",
        borderRadius: "var(--radius)",
        overflow: "hidden",
        border: "1px solid var(--border-color)",
      }}
    >
      <img
        src={heatmapUrl}
        alt="Crowd heatmap"
        style={{
          width: "100%",
          display: "block",
          aspectRatio: "16/9",
          objectFit: "cover",
        }}
      />
      {lastUpdated && (
        <div
          style={{
            position: "absolute",
            bottom: 8,
            right: 8,
            fontSize: "0.65rem",
            color: "var(--text-muted)",
            background: "rgba(0,0,0,0.6)",
            padding: "2px 8px",
            borderRadius: 4,
          }}
        >
          {lastUpdated.toLocaleTimeString()}
        </div>
      )}
    </div>
  );
}
