import { peticion } from "./api";

export async function solicitarMatricula(ofertasAcademicasIds) {
  return peticion("/matriculas/", {
    method: "POST",
    body: JSON.stringify({ ofertas_academicas_ids: ofertasAcademicasIds }),
  });
}

export async function listarMatriculas() {
  return peticion("/matriculas/");
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

export async function registrarPago(matriculaId) {
  return peticion(`/matriculas/${matriculaId}/pago`, { method: "POST" });
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