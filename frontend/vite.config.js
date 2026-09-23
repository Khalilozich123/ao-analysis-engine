import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The dev server runs in the container; polling makes file-watching reliable across the bind mount.
export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
    watch: { usePolling: true },
  },
});
