import { peticion } from "./api";

const URL_API = "http://localhost:5000/api/record-academico";

export async function obtenerRecord(estudianteId) {
  return peticion(`/record-academico/${estudianteId}`);
}

export async function miHistorial() {
  return peticion("/record-academico/historial-completo");
}

export function urlDescargarHistorialPdf() {
  return `${URL_API}/historial-completo/pdf`;
}

export async function obtenerProgreso(estudianteId) {
  return peticion(`/record-academico/progreso/${estudianteId}`);
}

export async function listarTiposClasificacion() {
  return peticion("/record-academico/tipos-clasificacion");
}

export async function listarEstadosPermanencia() {
  return peticion("/record-academico/estados-permanencia");
}
