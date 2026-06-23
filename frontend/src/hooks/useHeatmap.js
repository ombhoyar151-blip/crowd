import { useState, useEffect, useRef } from "react";
import { getHeatmapUrl } from "../api/heatmap";

export function useHeatmap(cameraId) {
  const [heatmapUrl, setHeatmapUrl] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const preloadRef = useRef(null);

  useEffect(() => {
    if (!cameraId) return;

    const tick = () => {
      const url = getHeatmapUrl(cameraId);
      const img = new Image();
      img.onload = () => {
        setHeatmapUrl(url);
        setLastUpdated(new Date());
      };
      img.onerror = () => {
        /* keep previous image on error */
      };
      img.src = url;
      preloadRef.current = img;
    };

    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [cameraId]);

  return { heatmapUrl, lastUpdated };
}
