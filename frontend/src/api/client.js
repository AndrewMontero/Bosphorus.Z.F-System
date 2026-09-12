/**
 * Cliente HTTP minimo.
 *
 * No guardamos ningun token: el backend los manda en cookies httpOnly que
 * JavaScript no puede leer. El navegador las adjunta solo. Por eso aca no
 * hay nada de localStorage ni de encabezados Authorization.
 */

class ErrorApi extends Error {
  constructor(mensaje, estado, datos) {
    super(mensaje);
    this.estado = estado;
    this.datos = datos;
  }
}

async function pedir(ruta, opciones = {}) {
  const respuesta = await fetch(`/api${ruta}`, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...(opciones.headers || {}) },
    ...opciones,
  });

  if (respuesta.status === 204) return null;

  let datos = null;
  try {
    datos = await respuesta.json();
  } catch {
    datos = null;
  }

  if (!respuesta.ok) {
    const detalle =
      datos?.detalle?.[0] || datos?.detalle || datos?.detail || "Ocurrió un error inesperado.";
    throw new ErrorApi(detalle, respuesta.status, datos);
  }

  return datos;
}

export const api = {
  get: (ruta) => pedir(ruta),
  post: (ruta, cuerpo) =>
    pedir(ruta, { method: "POST", body: cuerpo ? JSON.stringify(cuerpo) : undefined }),
};

export { ErrorApi };
