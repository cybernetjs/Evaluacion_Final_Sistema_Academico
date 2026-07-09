import { peticion } from "./api";

const URL_BASE = "http://localhost:5000/api";

export async function listarSolicitudes() {
  return peticion("/documentos/");
}

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
  return peticion(`/documentos/${certificadoId}/autorizar`, {
    method: "PUT",
  });


export async function emitirCertificado(certificadoId) {
  return peticion(`/documentos/${certificadoId}/emitir`, {
    method: "POST",
  });
}

export async function verificarCertificado(codigo) {
  return peticion(`/documentos/verificar/${codigo}`);
}

export function urlQrCertificado(codigo) {
  return `${URL_BASE}/documentos/qr/${codigo}`;
}