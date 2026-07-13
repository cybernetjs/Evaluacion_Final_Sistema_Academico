import { peticion } from "../../../nucleo/servicios/api";

const URL_BASE = "https://sistema-academico-backend-wfcn.onrender.com/api";

export async function listarCursos() {
  return peticion("/cursos/");
}

export async function obtenerCurso(id) {
  return peticion(`/cursos/${id}`);
}

export async function listarPrerequisitos() {
  return peticion("/cursos-docentes/prerequisitos");
}

export async function crearCurso(datos) {
  return peticion("/cursos/", {
    method: "POST",
    body: JSON.stringify(datos),
  });
}

export async function crearOfertaAcademica(datos) {
  return peticion("/ofertas-academicas/", {
    method: "POST",
    body: JSON.stringify(datos),
  });
}

export async function obtenerAsignacionesOferta(ofertaAcademicaId) {
  return peticion(`/cursos-docentes/ofertas/${ofertaAcademicaId}/asignaciones`);
}

export async function listarDocentes() {
  return peticion("/docentes/");
}

export async function listarTiposDocentes() {
  return peticion("/cursos-docentes/tipos-docentes");
}

export async function misCursosAsignados(periodoAcademicoId) {
  const parametros = new URLSearchParams();
  if (periodoAcademicoId) parametros.set("periodo_academico_id", periodoAcademicoId);
  return peticion(`/cursos-docentes/carga-academica?${parametros.toString()}`);
}

export async function periodosHistoricosDocente() {
  return peticion("/cursos-docentes/carga-academica/periodos-historicos");
}

export async function asignarDocente(ofertaAcademicaId, datos) {
  return peticion(`/cursos-docentes/ofertas/${ofertaAcademicaId}/asignar-docente`, {
    method: "POST",
    body: JSON.stringify(datos),
  });
}

export async function gestionarHorario(ofertaAcademicaId, datos) {
  return peticion(`/cursos-docentes/ofertas/${ofertaAcademicaId}/horario`, {
    method: "POST",
    body: JSON.stringify(datos),
  });
}

export async function cargaDocente(filtros = {}) {
  const parametros = new URLSearchParams();
  if (filtros.especialidadId) parametros.set("especialidad_id", filtros.especialidadId);
  if (filtros.periodoAcademicoId) parametros.set("periodo_academico_id", filtros.periodoAcademicoId);
  return peticion(`/cursos-docentes/carga-docente?${parametros.toString()}`);
}

export async function cargarSilabo(ofertaAcademicaId, archivo) {
  const token = localStorage.getItem("token");
  const formData = new FormData();
  formData.append("archivo", archivo);

  try {
    const respuesta = await fetch(`${URL_BASE}/cursos-docentes/ofertas/${ofertaAcademicaId}/silabo`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });

    const datos = await respuesta.json().catch(() => null);

    if (!respuesta.ok) {
      return { data: null, error: datos?.error || datos?.mensaje || "Ocurrió un error" };
    }

    return { data: datos, error: null };
  } catch {
    return { data: null, error: "No se pudo conectar con el servidor" };
  }
}

export async function cumplimientoSilabos(periodoAcademicoId) {
  const parametros = new URLSearchParams();
  if (periodoAcademicoId) parametros.set("periodo_academico_id", periodoAcademicoId);
  return peticion(`/cursos-docentes/auditoria/cumplimiento-silabos?${parametros.toString()}`);
}

export function urlDescargarSilabo(ofertaAcademicaId) {
  return `${URL_BASE}/cursos-docentes/ofertas/${ofertaAcademicaId}/silabo`;
}