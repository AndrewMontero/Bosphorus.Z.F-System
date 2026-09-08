import { defineStore } from "pinia";

import { api } from "@/api/client";

export const useAuth = defineStore("auth", {
  state: () => ({
    usuario: null,
    // Distingue "todavia no pregunte" de "pregunte y no hay sesion".
    // Sin esto, al recargar la pagina el guard rebotaria al login antes
    // de darle chance al backend de responder si la cookie sigue viva.
    sesionVerificada: false,
  }),

  getters: {
    autenticado: (estado) => estado.usuario !== null,
    permisos: (estado) => new Set(estado.usuario?.permisos ?? []),
    pantallaInicio: (estado) => estado.usuario?.pantalla_inicio || "/tablero",
    esSuperadmin: (estado) => estado.usuario?.es_superadmin === true,
  },

  actions: {
    puede(codigo) {
      return this.permisos.has(codigo);
    },

    async cargarSesion() {
      try {
        this.usuario = await api.get("/auth/yo/");
      } catch {
        this.usuario = null;
      } finally {
        this.sesionVerificada = true;
      }
      return this.usuario;
    },

    async login(email, password) {
      this.usuario = await api.post("/auth/login/", { email, password });
      this.sesionVerificada = true;
      return this.usuario;
    },

    async logout() {
      try {
        await api.post("/auth/logout/");
      } finally {
        this.usuario = null;
        this.sesionVerificada = true;
      }
    },
  },
});
