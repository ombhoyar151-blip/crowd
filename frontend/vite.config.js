import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    // Bind explicitly to IPv4 loopback so `127.0.0.1` works consistently
    host: "127.0.0.1",
    proxy: {
      "/api": "http://localhost:8000",
      "/ws": { target: "ws://localhost:8000", ws: true },
    },
  },
  // No custom esbuild loader mappings — use standard JSX handling
  // Configure esbuild for dev/build step
  esbuild: {
    jsx: "automatic",
  },
});
