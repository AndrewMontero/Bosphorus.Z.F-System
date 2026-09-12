import { createRouter, createWebHistory } from "vue-router";

import { useAuth } from "@/stores/auth";
import LoginView from "@/views/LoginView.vue";
import ModuloView from "@/views/ModuloView.vue";
import SinPermisoView from "@/views/SinPermisoView.vue";

const rutas = [
  { path: "/login", name: "login", component: LoginView, meta: { publica: true } },
  { path: "/sin-permiso", name: "sin-permiso", component: SinPermisoView },

  // Modulos: por ahora todos apuntan a la misma vista provisional. Cada uno
  // se ira reemplazando por su pantalla real en su propia rama.
  { path: "/paletizado", component: ModuloView, meta: { titulo: "Paletizado", permiso: "tarima:crear" } },
  { path: "/contenedores-del-dia", component: ModuloView, meta: { titulo: "Contenedores del día", permiso: "contenedor:crear" } },
  { path: "/lotes", component: ModuloView, meta: { titulo: "Lotes y fincas", permiso: "lote:leer" } },
  { path: "/facturacion", component: ModuloView, meta: { titulo: "Facturación", permiso: "factura:emitir" } },
  { path: "/asientos", component: ModuloView, meta: { titulo: "Asientos contables", permiso: "asiento:leer" } },
  { path: "/ordenes-pendientes", component: ModuloView, meta: { titulo: "Órdenes de compra", permiso: "orden_compra:crear" } },
  { path: "/planilla", component: ModuloView, meta: { titulo: "Planilla", permiso: "planilla:calcular" } },
  { path: "/tablero", component: ModuloView, meta: { titulo: "Tablero", permiso: "inventario:leer" } },
  { path: "/panel-superadmin", component: ModuloView, meta: { titulo: "Panel de administración", permiso: "usuario:asignar_rol" } },

  { path: "/", redirect: () => ({ name: "login" }) },
  { path: "/:resto(.*)*", redirect: () => ({ name: "login" }) },
];

export const router = createRouter({
  history: createWebHistory(),
  routes: rutas,
});

router.beforeEach(async (destino) => {
  const auth = useAuth();

  if (!auth.sesionVerificada) {
    await auth.cargarSesion();
  }

  if (destino.meta.publica) {
    // Ya con sesion, el login no tiene sentido: mandalo a lo suyo.
    return auth.autenticado ? auth.pantallaInicio : true;
  }

  if (!auth.autenticado) {
    return { name: "login", query: { destino: destino.fullPath } };
  }

  // Filtro de conveniencia. La defensa real esta en el backend, que valida
  // el permiso en cada peticion.
  if (destino.meta.permiso && !auth.puede(destino.meta.permiso)) {
    return { name: "sin-permiso" };
  }

  return true;
});
