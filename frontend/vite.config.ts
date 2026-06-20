import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev, proxy /api → the FastAPI backend so the frontend can use same-origin
// fetch with no CORS fuss. In prod, set VITE_API_BASE to the deployed backend.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
});
