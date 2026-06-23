import { useState, useEffect } from "react";
import { useAuth } from "../../hooks/useAuth";
import { getAlerts, resolveAlert } from "../../api/alerts";
import { useCameras } from "../../hooks/useCameras";
import AlertBadge from "../../components/AlertPanel/AlertBadge";
import Spinner from "../../components/common/Spinner";
import EmptyState from "../../components/common/EmptyState";
import GlassCard from "../../components/common/GlassCard";
import CameraSelector from "../../components/CameraSelector/CameraSelector";
import { formatDistanceToNow } from "date-fns";

export default function AlertsPage() {
  const { user } = useAuth();
  const { cameras } = useCameras();
  const [alerts, setAlerts] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [filter, setFilter] = useState({ severity: "", status: "", camera_id: "" });

  const fetchAlerts = async (p = 0) => {
    setLoading(true);
    try {
      const params = { limit: 50, offset: p * 50 };
      if (filter.severity) params.severity = filter.severity;
      if (filter.status === "unresolved") params.unresolved_only = true;
      if (filter.camera_id) params.camera_id = filter.camera_id;
      const data = await getAlerts(params);
      setAlerts(data.items || []);
      setTotal(data.total || 0);
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts(page);
  }, [page, filter]);

  const handleResolve = async (id) => {
    await resolveAlert(id);
    setAlerts((prev) =>
      prev.map((a) =>
        a.id === id ? { ...a, resolved_at: new Date().toISOString() } : a
      )
    );
  };

  const totalPages = Math.ceil(total / 50);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <GlassCard>
        <div
          style={{
            display: "flex",
            gap: 10,
            flexWrap: "wrap",
            alignItems: "center",
          }}
        >
          <CameraSelector
            cameras={cameras}
            value={filter.camera_id}
            onChange={(v) => setFilter((f) => ({ ...f, camera_id: v }))}
          />
          <select
            value={filter.severity}
            onChange={(e) =>
              setFilter((f) => ({ ...f, severity: e.target.value }))
            }
            style={{
              padding: "6px 12px",
              borderRadius: 8,
              border: "1px solid var(--border-color)",
              background: "var(--bg-surface)",
              color: "var(--text-primary)",
              fontSize: "0.8125rem",
              fontFamily: "inherit",
              outline: "none",
            }}
          >
            <option value="">All Severity</option>
            <option value="warning">Warning</option>
            <option value="critical">Critical</option>
          </select>
          <select
            value={filter.status}
            onChange={(e) =>
              setFilter((f) => ({ ...f, status: e.target.value }))
            }
            style={{
              padding: "6px 12px",
              borderRadius: 8,
              border: "1px solid var(--border-color)",
              background: "var(--bg-surface)",
              color: "var(--text-primary)",
              fontSize: "0.8125rem",
              fontFamily: "inherit",
              outline: "none",
            }}
          >
            <option value="">All Status</option>
            <option value="unresolved">Unresolved</option>
          </select>
          <span style={{ fontSize: "0.8125rem", color: "var(--text-muted)" }}>
            {total} total
          </span>
        </div>
      </GlassCard>

      {loading && <Spinner />}

      {!loading && alerts.length === 0 && <EmptyState message="No alerts found" />}

      {!loading && alerts.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {alerts.map((alert) => (
            <GlassCard key={alert.id} style={{ padding: "12px 16px" }}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                }}
              >
                <AlertBadge severity={alert.severity} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div
                    style={{
                      fontSize: "0.875rem",
                      fontWeight: 500,
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
                    {alert.camera_id} \u00B7 {alert.count}/{alert.threshold}
                    \u00B7{" "}
                    {formatDistanceToNow(new Date(alert.time), {
                      addSuffix: true,
                    })}
                  </div>
                  <div
                    style={{
                      fontSize: "0.75rem",
                      color: "var(--text-muted)",
                      marginTop: 2,
                    }}
                  >
                    {alert.message}
                  </div>
                </div>
                {!alert.resolved_at && user?.role === "admin" && (
                  <button
                    onClick={() => handleResolve(alert.id)}
                    style={{
                      padding: "6px 14px",
                      borderRadius: 6,
                      border: "1px solid var(--border-color)",
                      background: "transparent",
                      color: "var(--accent)",
                      fontSize: "0.75rem",
                      fontWeight: 500,
                      cursor: "pointer",
                      transition: "var(--transition)",
                      whiteSpace: "nowrap",
                    }}
                    onMouseEnter={(e) =>
                      (e.target.style.background = "rgba(99,102,241,0.1)")
                    }
                    onMouseLeave={(e) =>
                      (e.target.style.background = "transparent")
                    }
                  >
                    Resolve
                  </button>
                )}
                {alert.resolved_at && (
                  <span
                    style={{
                      fontSize: "0.7rem",
                      color: "var(--text-muted)",
                      whiteSpace: "nowrap",
                    }}
                  >
                    Resolved
                  </span>
                )}
              </div>
            </GlassCard>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: 8,
            marginTop: 8,
          }}
        >
          <button
            disabled={page === 0}
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            style={{
              padding: "6px 14px",
              borderRadius: 6,
              border: "1px solid var(--border-color)",
              background: "transparent",
              color: page === 0 ? "var(--text-muted)" : "var(--text-primary)",
              cursor: page === 0 ? "not-allowed" : "pointer",
              fontSize: "0.8125rem",
            }}
          >
            Previous
          </button>
          <span
            style={{
              fontSize: "0.8125rem",
              color: "var(--text-muted)",
              alignSelf: "center",
            }}
          >
            Page {page + 1} of {totalPages}
          </span>
          <button
            disabled={page >= totalPages - 1}
            onClick={() => setPage((p) => p + 1)}
            style={{
              padding: "6px 14px",
              borderRadius: 6,
              border: "1px solid var(--border-color)",
              background: "transparent",
              color:
                page >= totalPages - 1
                  ? "var(--text-muted)"
                  : "var(--text-primary)",
              cursor:
                page >= totalPages - 1 ? "not-allowed" : "pointer",
              fontSize: "0.8125rem",
            }}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
