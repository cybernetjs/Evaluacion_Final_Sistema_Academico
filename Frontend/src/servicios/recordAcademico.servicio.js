import { peticion } from "./api";

export async function obtenerRecord(estudianteId) {
  return peticion(`/record-academico/${estudianteId}`);
}

export async function miHistorial() {
  return peticion("/record-academico/historial-completo");
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
