import client from "./client";

export async function login(username, password) {
  const res = await client.post("/api/v1/auth/token", { username, password });
  return res.data;
}

export async function getMe() {
  const res = await client.get("/api/v1/auth/me");
  return res.data;
}
