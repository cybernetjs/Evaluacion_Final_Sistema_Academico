import { peticion } from "./api";

export async function solicitarMatricula(datos) {
  return peticion("/matriculas/", {
    method: "POST",
    body: JSON.stringify(datos),
  });
}

export async function listarMatriculas() {
  return peticion("/matriculas/");
}

export async function listarPeriodos() {
  return peticion("/matriculas/periodos");
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