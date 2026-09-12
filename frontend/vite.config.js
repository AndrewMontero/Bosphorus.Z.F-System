import { fileURLToPath, URL } from "node:url";

import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) },
  },
  server: {
    host: "0.0.0.0",
    port: 5173,
    // El proxy hace que el navegador vea todo en el mismo origen. Sin esto,
    // la cookie httpOnly con SameSite=Lax no viajaria en las peticiones
    // (5173 -> 8000 seria cruzado) y habria que abrir CORS y bajar SameSite,
    // que es justo lo que no queremos.
    proxy: {
      "/api": { target: "http://backend:8000", changeOrigin: true },
      "/admin": { target: "http://backend:8000", changeOrigin: true },
      "/static": { target: "http://backend:8000", changeOrigin: true },
    },
  },
});
