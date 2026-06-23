import { useState, useContext } from "react";
import { CameraContext } from "../../context/CameraContext";
import { useAnalytics } from "../../hooks/useAnalytics";
import { subMinutes, startOfDay, formatISO } from "date-fns";
import GlassCard from "../../components/common/GlassCard";
import CountChart from "../../components/CountChart/CountChart";
import DensityChart from "../../components/DensityChart/DensityChart";
import ZoneHistoryChart from "../../components/ZoneHistoryChart/ZoneHistoryChart";
import Spinner from "../../components/common/Spinner";

const presets = [
  { label: "5 min", getFrom: () => subMinutes(new Date(), 5) },
  { label: "15 min", getFrom: () => subMinutes(new Date(), 15) },
  { label: "1 hour", getFrom: () => subMinutes(new Date(), 60) },
  { label: "Today", getFrom: () => startOfDay(new Date()) },
];

export default function AnalyticsPage() {
  const { cameraId } = useContext(CameraContext);
  const [preset, setPreset] = useState(2);
  const [autoRefresh, setAutoRefresh] = useState(false);

  const from = presets[preset].getFrom();
  const { data, summary, loading, refetch } = useAnalytics({
    cameraId,
    from: formatISO(from),
    to: formatISO(new Date()),
    limit: 500,
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 8,
        }}
      >
        <div style={{ display: "flex", gap: 6 }}>
          {presets.map((p, i) => (
            <button
              key={p.label}
              onClick={() => setPreset(i)}
              style={{
                padding: "6px 14px",
                borderRadius: 8,
                border: "1px solid var(--border-color)",
                background:
                  preset === i ? "rgba(99,102,241,0.15)" : "transparent",
                color:
                  preset === i ? "var(--accent)" : "var(--text-muted)",
                fontSize: "0.8125rem",
                fontWeight: 500,
                cursor: "pointer",
                transition: "var(--transition)",
              }}
            >
              {p.label}
            </button>
          ))}
        </div>

        <label
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            fontSize: "0.8125rem",
            color: "var(--text-muted)",
            cursor: "pointer",
          }}
        >
          <input
            type="checkbox"
            checked={autoRefresh}
            onChange={(e) => setAutoRefresh(e.target.checked)}
            style={{ accentColor: "var(--accent)" }}
          />
          Auto-refresh
        </label>
      </div>

      {loading && <Spinner />}

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
          Person Count Over Time
        </h3>
        <CountChart data={data} loading={loading} />
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
          Density Score Over Time
        </h3>
        <DensityChart data={data} loading={loading} />
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
          Zone Occupancy History
        </h3>
        <ZoneHistoryChart data={data} loading={loading} />
      </GlassCard>

      {summary && (
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
            Summary
          </h3>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(3, 1fr)",
              gap: 12,
            }}
          >
            <div>
              <div
                style={{
                  fontSize: "0.75rem",
                  color: "var(--text-muted)",
                  marginBottom: 2,
                }}
              >
                Average
              </div>
              <div
                style={{
                  fontSize: "1.25rem",
                  fontWeight: 700,
                  fontFamily: "var(--font-mono)",
                  color: "var(--accent)",
                }}
              >
                {summary.avg_count?.toFixed(1) || "-"}
              </div>
            </div>
            <div>
              <div
                style={{
                  fontSize: "0.75rem",
                  color: "var(--text-muted)",
                  marginBottom: 2,
                }}
              >
                Max
              </div>
              <div
                style={{
                  fontSize: "1.25rem",
                  fontWeight: 700,
                  fontFamily: "var(--font-mono)",
                  color: "var(--warning)",
                }}
              >
                {summary.max_count ?? "-"}
              </div>
            </div>
            <div>
              <div
                style={{
                  fontSize: "0.75rem",
                  color: "var(--text-muted)",
                  marginBottom: 2,
                }}
              >
                Min
              </div>
              <div
                style={{
                  fontSize: "1.25rem",
                  fontWeight: 700,
                  fontFamily: "var(--font-mono)",
                  color: "var(--success)",
                }}
              >
                {summary.min_count ?? "-"}
              </div>
            </div>
          </div>
        </GlassCard>
      )}
    </div>
  );
}
