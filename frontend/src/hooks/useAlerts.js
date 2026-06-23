import { useState, useEffect, useCallback, useRef } from "react";
import { getAlerts, resolveAlert as apiResolve } from "../api/alerts";
import { showAlertToast } from "../components/AlertToast/alertToast";

export function useAlerts({ subscribe, cameraId, filters = {} } = {}) {
  const [liveAlerts, setLiveAlerts] = useState([]);
  const [historicalAlerts, setHistoricalAlerts] = useState([]);
  const [unresolvedCount, setUnresolvedCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const seenRef = useRef(new Set());

  const fetchHistorical = useCallback(
    async (page = 0) => {
      setLoading(true);
      try {
        const params = { limit: 50, offset: page * 50 };
        if (cameraId) params.camera_id = cameraId;
        if (filters.severity) params.severity = filters.severity;
        if (filters.status === "unresolved") params.unresolved_only = true;
        if (filters.from) params.from_ts = filters.from;
        if (filters.to) params.to_ts = filters.to;

        const data = await getAlerts(params);
        setHistoricalAlerts(data.items || []);
        setTotal(data.total || 0);
        setUnresolvedCount(
          (data.items || []).filter((a) => !a.resolved_at).length
        );
      } catch {
        /* ignore */
      } finally {
        setLoading(false);
      }
    },
    [cameraId, filters]
  );

  useEffect(() => {
    if (!cameraId && !filters.severity) return;
    fetchHistorical(0);
  }, [fetchHistorical, cameraId]);

  useEffect(() => {
    if (!subscribe) return;
    const unsub = subscribe("alert", (data) => {
      if (seenRef.current.has(data.alert_id)) return;
      seenRef.current.add(data.alert_id);
      setLiveAlerts((prev) => [data, ...prev].slice(0, 50));
      setUnresolvedCount((c) => c + 1);
      showAlertToast(data);
    });
    return unsub;
  }, [subscribe]);

  const resolve = useCallback(async (id) => {
    try {
      await apiResolve(id);
      setHistoricalAlerts((prev) =>
        prev.map((a) => (a.id === id ? { ...a, resolved_at: new Date().toISOString() } : a))
      );
      setLiveAlerts((prev) =>
        prev.map((a) => (a.alert_id === id ? { ...a, resolved_at: new Date().toISOString() } : a))
      );
      setUnresolvedCount((c) => Math.max(0, c - 1));
    } catch {
      /* ignore */
    }
  }, []);

  return {
    liveAlerts,
    historicalAlerts,
    unresolvedCount,
    total,
    loading,
    fetchHistorical,
    resolve,
  };
}
