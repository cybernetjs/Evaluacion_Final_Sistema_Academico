import { peticion } from "./api";

const URL_BASE = "http://localhost:5000/api";

export async function solicitarDocumento(tipo, archivo) {
  const formData = new FormData();
  formData.append("tipo", tipo);
  formData.append("comprobante", archivo);

  const token = localStorage.getItem("token");
  const respuesta = await fetch(`${URL_BASE}/documentos/solicitar`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });

  const cuerpo = await respuesta.json().catch(() => null);
  if (!respuesta.ok) {
    return { data: null, error: cuerpo?.error || "No se pudo registrar la solicitud" };
  }
  return { data: cuerpo, error: null };
}

export async function misSolicitudes() {
  return peticion("/documentos/mis-solicitudes");
}

export async function bandeja(filtros = {}) {
  const parametros = new URLSearchParams();
  if (filtros.estado) parametros.set("estado", filtros.estado);
  if (filtros.pagina) parametros.set("pagina", filtros.pagina);
  if (filtros.porPagina) parametros.set("por_pagina", filtros.porPagina);
  const query = parametros.toString();
  return peticion(`/documentos/bandeja${query ? `?${query}` : ""}`);
}

export async function detalleExpediente(certificadoId) {
  return peticion(`/documentos/${certificadoId}/expediente`);
}

export function urlComprobante(certificadoId) {
  return `${URL_BASE}/documentos/${certificadoId}/comprobante`;
}

// El comprobante está protegido por JWT, así que no se puede cargar
// directamente en un <iframe src="..."> (el navegador no envía el
// Authorization header en esa petición). Lo descargamos manualmente
// con fetch (que sí incluye el token) y devolvemos un blob URL local
// para usar como src del iframe.
export async function obtenerComprobanteBlobUrl(certificadoId) {
  const token = localStorage.getItem("token");
  try {
    const respuesta = await fetch(`${URL_BASE}/documentos/${certificadoId}/comprobante`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });

    if (!respuesta.ok) {
      return { data: null, error: "No se pudo cargar el comprobante" };
    }

    const blob = await respuesta.blob();
    return { data: URL.createObjectURL(blob), error: null };
  } catch {
    return { data: null, error: "No se pudo conectar con el servidor" };
  }
}

export async function aprobarTramite(certificadoId) {
  return peticion("/documentos/tramite/aprobar", {
    method: "PUT",
    body: JSON.stringify({ id: certificadoId }),
  });
}

export async function rechazarTramite(certificadoId, motivo) {
  return peticion("/documentos/tramite/rechazar", {
    method: "PUT",
    body: JSON.stringify({ id: certificadoId, motivo }),
  });
}

export async function firmarCertificados(certificadoIds) {
  return peticion("/documentos/firmar", {
    method: "POST",
    body: JSON.stringify({ certificado_ids: certificadoIds }),
  });
}

export function urlDescargarCertificadoEmitido(certificadoId) {
  return `${URL_BASE}/documentos/${certificadoId}/descargar`;
}

export async function verificarCertificado(codigo) {
  return peticion(`/documentos/verificar/${codigo}`);
}