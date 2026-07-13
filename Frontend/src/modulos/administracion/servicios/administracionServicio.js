import { peticion } from "../../../nucleo/servicios/api";

export async function listarUsuarios() {
  return peticion("/administracion/usuarios");
}

export async function cambiarRol(usuarioId, rol) {
  return peticion(`/administracion/usuarios/${usuarioId}/rol`, {
    method: "PUT",
    body: JSON.stringify({ rol }),
  });
}

export async function registrarDocente(datosDocente) {
  return peticion("/administracion/docentes", {
    method: "POST",
    body: JSON.stringify(datosDocente),
  });
}

export async function registrarPersonal(datosPersonal) {
  return peticion("/administracion/personal", {
    method: "POST",
    body: JSON.stringify(datosPersonal),
  });
}

export async function listarAuditorias() {
  return peticion("/administracion/auditorias");
}

export async function reportesEstrategicos() {
  return peticion("/administracion/reportes-estrategicos");
}

export async function listarFacultades() {
  return peticion("/administracion/facultades");
}

export async function listarEspecialidades() {
  return peticion("/administracion/especialidades");
}

export async function listarPlanesEstudio() {
  return peticion("/administracion/planes-estudio");
}

export async function listarSemestres() {
  return peticion("/administracion/semestres");
}

export async function listarPeriodos() {
  return peticion("/administracion/periodos");
}

export async function obtenerConfiguracionCiclo() {
  return peticion("/admin/configuracion/ciclo-global");
}

export async function actualizarConfiguracionCiclo(datos) {
  return peticion("/admin/configuracion/ciclo-global", {
    method: "PUT",
    body: JSON.stringify(datos),
  });
}

export async function obtenerMatrizPermisos() {
  return peticion("/administracion/permisos");
}

export async function actualizarMatrizPermisos(cambios) {
  return peticion("/administracion/permisos", {
    method: "PUT",
    body: JSON.stringify({ permisos: cambios }),
  });
}