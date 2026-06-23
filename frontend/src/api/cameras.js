import client from "./client";

export async function getCameras() {
  const res = await client.get("/api/v1/cameras");
  return res.data;
}
