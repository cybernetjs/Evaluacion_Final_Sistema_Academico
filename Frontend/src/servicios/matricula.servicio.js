import { peticion } from "./api";

export async function solicitarMatricula(ofertasAcademicasIds) {
  return peticion("/matriculas/", {
    method: "POST",
    body: JSON.stringify({ ofertas_academicas_ids: ofertasAcademicasIds }),
  });
}

export async function listarMatriculas(filtros = {}) {
  const parametros = new URLSearchParams();
  if (filtros.periodoId) parametros.set("periodo_id", filtros.periodoId);
  if (filtros.especialidadId) parametros.set("especialidad_id", filtros.especialidadId);
  if (filtros.estado) parametros.set("estado", filtros.estado);
  if (filtros.pagina) parametros.set("pagina", filtros.pagina);
  if (filtros.porPagina) parametros.set("por_pagina", filtros.porPagina);

  const query = parametros.toString();
  return peticion(`/matriculas/${query ? `?${query}` : ""}`);
}

export async function validarPeriodo(estudianteId) {
  return peticion(`/matriculas/validar-periodo/${estudianteId}`);
}

export async function cancelarMatricula(matriculaId) {
  return peticion("/matriculas/cancelar", {
    method: "POST",
    body: JSON.stringify({ matricula_id: matriculaId }),
  });
}

export async function listarPeriodos() {
  return peticion("/matriculas/periodos");
}

export async function obtenerPeriodoActual() {
  return peticion("/matriculas/periodo-actual");
}

export async function obtenerCursosDisponibles() {
  return peticion("/matriculas/cursos-disponibles");
}

export async function obtenerMiSolicitudActual() {
  return peticion("/matriculas/mi-solicitud-actual");
}

export function urlDescargarFichaPreliminar() {
  return "http://localhost:5000/api/matriculas/ficha-preliminar/descargar";
}

export async function listarOfertas() {
  return peticion("/matriculas/ofertas");
}

export async function listarEstadosMatricula() {
  return peticion("/matriculas/estados");
}

export async function validarRequisitos(matriculaId) {
  return peticion(`/matriculas/${matriculaId}/validar`, { method: "PUT" });
}

export async function registrarPago(matriculaId, datosPago) {
  const formData = new FormData();
  formData.append("numero_operacion", datosPago.numeroOperacion);
  formData.append("fecha_pago", datosPago.fechaPago);
  formData.append("monto", datosPago.monto);
  formData.append("comprobante", datosPago.archivo);

  const token = localStorage.getItem("token");
  const respuesta = await fetch(`http://localhost:5000/api/matriculas/${matriculaId}/pago`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });

  const cuerpo = await respuesta.json().catch(() => null);
  if (!respuesta.ok) {
    return { data: null, error: cuerpo?.error || "No se pudo registrar el pago" };
  }
  return { data: cuerpo, error: null };
}

export async function generarFichaOficial(matriculaId) {
  return peticion(`/matriculas/${matriculaId}/ficha-oficial`, { method: "POST" });
}

export async function obtenerEstadisticas() {
  return peticion("/matriculas/estadisticas");
}

export function urlDescargarFicha(matriculaId) {
  return `http://localhost:5000/api/matriculas/${matriculaId}/ficha`;
}