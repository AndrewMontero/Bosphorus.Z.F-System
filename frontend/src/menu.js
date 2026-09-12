/**
 * El menu vive en codigo, no en una tabla de configuracion.
 *
 * En MiFiNet el menu se arma desde la base de datos, y por eso
 * "Facturacion y Ventas" aparece duplicado en Catalogos: es un dato mal
 * cargado que nadie valido. Aca un duplicado seria un error visible en el
 * codigo, no un registro suelto en produccion.
 *
 * Cada entrada declara el permiso que la habilita. Lo que el usuario ve se
 * filtra con los permisos que el backend reporta -- pero eso es comodidad
 * visual: quien manda es la verificacion del servidor en cada peticion.
 */

export const MENU = [
  {
    dominio: "Producción y empaque",
    entradas: [
      { texto: "Paletizado", ruta: "/paletizado", permiso: "tarima:crear" },
      { texto: "Contenedores", ruta: "/contenedores-del-dia", permiso: "contenedor:crear" },
    ],
  },
  {
    dominio: "Agrícola",
    entradas: [{ texto: "Lotes y fincas", ruta: "/lotes", permiso: "lote:leer" }],
  },
  {
    dominio: "Facturación",
    entradas: [{ texto: "Facturación", ruta: "/facturacion", permiso: "factura:emitir" }],
  },
  {
    dominio: "Contabilidad",
    entradas: [{ texto: "Asientos", ruta: "/asientos", permiso: "asiento:leer" }],
  },
  {
    dominio: "Proveeduría",
    entradas: [
      { texto: "Órdenes de compra", ruta: "/ordenes-pendientes", permiso: "orden_compra:crear" },
    ],
  },
  {
    dominio: "Recursos humanos",
    entradas: [{ texto: "Planilla", ruta: "/planilla", permiso: "planilla:calcular" }],
  },
  {
    dominio: "Consulta",
    entradas: [{ texto: "Tablero", ruta: "/tablero", permiso: "inventario:leer" }],
  },
  {
    dominio: "Sistema",
    entradas: [
      { texto: "Panel de administración", ruta: "/panel-superadmin", permiso: "usuario:asignar_rol" },
    ],
  },
];
