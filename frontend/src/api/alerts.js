import client from "./client";

export async function getAlerts(params = {}) {
  const res = await client.get("/api/v1/alerts", { params });
  return res.data;
}

export async function resolveAlert(id) {
  const res = await client.patch(`/api/v1/alerts/${id}/resolve`);
  return res.data;
}
