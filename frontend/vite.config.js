import { defineConfig } from "vite";

export default defineConfig({
  server: {
    proxy: {
      "/tickets": "http://localhost:8000",
      "/chat": "http://localhost:8001",
    },
  },
});
