const URL_BASE = "http://localhost:5000/api";

export async function peticion(ruta, opciones = {}) {
  const token = localStorage.getItem("token");

  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...opciones.headers,
  };

  try {
    const respuesta = await fetch(`${URL_BASE}${ruta}`, {
      ...opciones,
      headers,
    });

    const datos = await respuesta.json().catch(() => null);

    if (!respuesta.ok) {
      if ((respuesta.status === 401 || respuesta.status === 422) && datos?.msg) {
        localStorage.removeItem("token");
        localStorage.removeItem("usuario");
        return { data: null, error: "Tu sesion vencio. Inicia sesion nuevamente." };
      }

      return { data: null, error: datos?.error || datos?.mensaje || datos?.msg || "Ocurrio un error" };
    }

    return { data: datos, error: null };
  } catch (err) {
    return { data: null, error: "No se pudo conectar con el servidor" };
  }
}
