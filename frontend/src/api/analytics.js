import client from "./client";

export async function getHistory(cameraId, { from, to, limit = 500 } = {}) {
  const params = { camera_id: cameraId, limit };
  if (from) params.from = from;
  if (to) params.to = to;
  const res = await client.get("/api/v1/analytics/history", { params });
  return res.data;
}

export async function getCurrent(cameraId) {
  const res = await client.get("/api/v1/analytics/current", {
    params: { camera_id: cameraId },
  });
  return res.data;
}

export async function getSummary(cameraId) {
  const res = await client.get("/api/v1/analytics/summary", {
    params: { camera_id: cameraId },
  });
  return res.data;
}
