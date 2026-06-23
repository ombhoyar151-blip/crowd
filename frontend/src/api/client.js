import axios from "axios";

const client = axios.create({
  // Use VITE_API_URL when set; otherwise make requests absolute so
  // paths like `/api/v1/...` are sent to the dev server (and proxied).
  baseURL: import.meta.env.VITE_API_URL || "",
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default client;
