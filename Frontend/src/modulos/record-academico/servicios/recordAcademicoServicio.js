import { peticion } from "../../../nucleo/servicios/api";

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

export async function listarAniosIngreso() {
  return peticion("/record-academico/anios-ingreso");
}

export async function reportesConsolidados(filtros = {}) {
  const parametros = new URLSearchParams();
  if (filtros.anioIngreso) parametros.set("anio_ingreso", filtros.anioIngreso);
  if (filtros.especialidadId) parametros.set("especialidad_id", filtros.especialidadId);
  if (filtros.estado) parametros.set("estado", filtros.estado);
  return peticion(`/record-academico/reportes?${parametros.toString()}`);
}

export function urlExportarReportesXlsx(filtros = {}) {
  const parametros = new URLSearchParams();
  if (filtros.anioIngreso) parametros.set("anio_ingreso", filtros.anioIngreso);
  if (filtros.especialidadId) parametros.set("especialidad_id", filtros.especialidadId);
  if (filtros.estado) parametros.set("estado", filtros.estado);
  return `${URL_API}/reportes/exportar?${parametros.toString()}`;
}

export async function analisisCohorte(especialidadId, anios = []) {
  const parametros = new URLSearchParams();
  if (especialidadId) parametros.set("especialidad_id", especialidadId);
  if (anios.length) parametros.set("anios", anios.join(","));
  return peticion(`/record-academico/analisis-cohorte?${parametros.toString()}`);
}