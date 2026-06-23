export function getHeatmapUrl(cameraId) {
  const base = import.meta.env.VITE_API_URL || "/api";
  return `${base}/api/v1/heatmap/${cameraId}?t=${Date.now()}`;
}
