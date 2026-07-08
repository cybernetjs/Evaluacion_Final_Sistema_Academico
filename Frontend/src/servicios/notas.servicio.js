import { peticion } from "./api";

export async function listarNotas() {
  return peticion("/notas/");
}

export async function obtenerPlanilla(ofertaAcademicaId) {
  return peticion(`/notas/planilla/${ofertaAcademicaId}`);
}

export async function estadoCronograma(ofertaAcademicaId, tipoNota) {
  return peticion(`/notas/cronograma/${ofertaAcademicaId}?tipo_nota=${tipoNota}`);
}

export async function registrarNotasPlanilla(ofertaAcademicaId, tipoNota, calificaciones) {
  return peticion("/notas/registro", {
    method: "PUT",
    body: JSON.stringify({
      oferta_academica_id: ofertaAcademicaId,
      tipo_nota: tipoNota,
      calificaciones,
    }),
  });
}

export async function obtenerNotasMatricula(matriculaId) {
  return peticion(`/notas/matricula/${matriculaId}`);
}

export async function miHojaDeNotas(semestreId) {
  const query = semestreId ? `?semestre_id=${semestreId}` : "";
  return peticion(`/notas/mi-hoja${query}`);
}

export async function obtenerCiclosCursados() {
  return peticion("/notas/ciclos-cursados");
}

export async function obtenerHojaCiclo(periodoAcademicoId) {
  const query = periodoAcademicoId ? `?periodo_academico_id=${periodoAcademicoId}` : "";
  return peticion(`/notas/hoja-ciclo${query}`);
}

export async function publicarNotas(ofertaAcademicaId) {
  return peticion("/notas/publicar", {
    method: "POST",
    body: JSON.stringify({ oferta_academica_id: ofertaAcademicaId }),
  });
}

export async function registrarNota(datos) {
  return peticion("/notas/", {
    method: "PUT",
    body: JSON.stringify(datos),
  });
}

export async function listarEstadosCurso() {
  return peticion("/notas/estados");
}

export async function panelActas() {
  return peticion("/notas/actas");
}

export async function alumnosOmisos(ofertaAcademicaId) {
  return peticion(`/notas/actas/${ofertaAcademicaId}/omisos`);
}

export async function cerrarActa(ofertaAcademicaId) {
  return peticion("/notas/actas/cerrar", {
    method: "POST",
    body: JSON.stringify({ oferta_academica_id: ofertaAcademicaId }),
  });
}

export async function indicadoresAcademicos() {
  return peticion("/notas/indicadores");
}