import { useState, useEffect, useCallback } from "react";
import { getHistory, getSummary } from "../api/analytics";

export function useAnalytics({ cameraId, from, to, limit = 500 } = {}) {
  const [data, setData] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const refetch = useCallback(async () => {
    if (!cameraId) return;
    setLoading(true);
    setError(null);
    try {
      const hist = await getHistory(cameraId, { from, to, limit });
      setData(hist.items || []);
      const summ = await getSummary(cameraId);
      setSummary(summ);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to fetch analytics");
    } finally {
      setLoading(false);
    }
  }, [cameraId, from, to, limit]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { data, summary, loading, error, refetch };
}
