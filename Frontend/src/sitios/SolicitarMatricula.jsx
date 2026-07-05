import { useState, useEffect } from "react";
import {
  solicitarMatricula,
  obtenerPeriodoActual,
  obtenerCursosDisponibles,
  urlDescargarFicha,
} from "../servicios/matricula.servicio";

const NOMBRES_DIA = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];

function hayConflictoHorario(cursoA, cursoB) {
  for (const h1 of cursoA.horarios) {
    for (const h2 of cursoB.horarios) {
      if (h1.dia === h2.dia && h1.hora_inicio < h2.hora_fin && h1.hora_fin > h2.hora_inicio) {
        return true;
      }
    }
  }
  return false;
}

export default function SolicitarMatricula() {
  const [periodo, setPeriodo] = useState(null);
  const [datosCursos, setDatosCursos] = useState(null);
  const [seleccionados, setSeleccionados] = useState([]);
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);
  const [ultimaMatriculaId, setUltimaMatriculaId] = useState(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    cargarDatos();
  }, []);

  async function cargarDatos() {
    setCargando(true);
    const [resPeriodo, resCursos] = await Promise.all([
      obtenerPeriodoActual(),
      obtenerCursosDisponibles(),
    ]);

    if (!resPeriodo.error) setPeriodo(resPeriodo.data);
    if (!resCursos.error) setDatosCursos(resCursos.data);
    if (resCursos.error) setError(resCursos.error);

    setCargando(false);
  }

  function cursoEstaSeleccionado(cursoId) {
    return seleccionados.some((c) => c.oferta_academica_id === cursoId);
  }

  function tieneConflictoConSeleccionados(curso) {
    return seleccionados.some((s) => hayConflictoHorario(s, curso));
  }

  const creditosSeleccionados = seleccionados.reduce((total, c) => total + c.creditos, 0);
  const creditosMaximos = datosCursos?.creditos_maximos_por_ciclo ?? 0;

  function excedeCreditos(curso) {
    return creditosSeleccionados + curso.creditos > creditosMaximos;
  }

  function manejarToggle(curso) {
    setError(null);
    const yaSeleccionado = cursoEstaSeleccionado(curso.oferta_academica_id);

    if (yaSeleccionado) {
      setSeleccionados(seleccionados.filter((c) => c.oferta_academica_id !== curso.oferta_academica_id));
      return;
    }

    if (!curso.habilitado) return;
    if (tieneConflictoConSeleccionados(curso)) return;
    if (excedeCreditos(curso)) return;

    setSeleccionados([...seleccionados, curso]);
  }

  async function manejarEnvio() {
    setMensaje(null);
    setError(null);

    if (seleccionados.length === 0) {
      setError("Selecciona al menos un curso antes de enviar la solicitud");
      return;
    }

    const ids = seleccionados.map((c) => c.oferta_academica_id);
    const { data, error } = await solicitarMatricula(ids);

    if (error) {
      setError(error);
      return;
    }

    setMensaje(`Solicitud registrada correctamente. N° de matrícula: ${data.id} — Créditos: ${data.total_creditos}`);
    setUltimaMatriculaId(data.id);
    setSeleccionados([]);
    cargarDatos();
  }

  async function manejarDescargaFicha() {
    const token = localStorage.getItem("token");
    const respuesta = await fetch(urlDescargarFicha(ultimaMatriculaId), {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!respuesta.ok) {
      setError("No se pudo descargar la ficha");
      return;
    }

    const blob = await respuesta.blob();
    const url = window.URL.createObjectURL(blob);
    const enlace = document.createElement("a");
    enlace.href = url;
    enlace.download = `ficha_matricula_${ultimaMatriculaId}.pdf`;
    enlace.click();
    window.URL.revokeObjectURL(url);
  }

  function renderizarGrupo(titulo, tipo) {
    const cursos = datosCursos.cursos.filter((c) => c.tipo === tipo);
    if (cursos.length === 0) return null;

    return (
      <div style={{ marginBottom: 20 }}>
        <h3 style={{ fontSize: 14, marginBottom: 8 }}>{titulo}</h3>
        <table>
          <thead>
            <tr>
              <th></th>
              <th>Curso</th>
              <th>Créditos</th>
              <th>Horario</th>
            </tr>
          </thead>
          <tbody>
            {cursos.map((curso) => {
              const seleccionado = cursoEstaSeleccionado(curso.oferta_academica_id);
              const conflicto = !seleccionado && tieneConflictoConSeleccionados(curso);
              const sinCreditos = !seleccionado && excedeCreditos(curso);
              const bloqueado = !curso.habilitado || conflicto || sinCreditos;

              let motivo = curso.motivo_bloqueo;
              if (curso.habilitado && conflicto) motivo = "Cruce de horario con un curso ya seleccionado";
              if (curso.habilitado && sinCreditos) motivo = "Excede el máximo de créditos permitidos";

              return (
                <tr
                  key={curso.oferta_academica_id ?? curso.curso_id}
                  title={bloqueado ? motivo : undefined}
                  style={bloqueado ? { color: "#ff6b6b" } : undefined}
                >
                  <td>
                    <input
                      type="checkbox"
                      checked={seleccionado}
                      disabled={bloqueado && !seleccionado}
                      onChange={() => manejarToggle(curso)}
                    />
                  </td>
                  <td>
                    {bloqueado && !seleccionado ? "⚠ " : ""}
                    {curso.curso_nombre}
                  </td>
                  <td>{curso.creditos}</td>
                  <td>
                    {curso.horarios.length === 0
                      ? "Sin horario"
                      : curso.horarios
                          .map((h) => `${NOMBRES_DIA[h.dia] ?? h.dia} ${h.hora_inicio}-${h.hora_fin}`)
                          .join(" / ")}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    );
  }

  if (cargando) return <div className="contenedor"><p>Cargando...</p></div>;

  return (
    <div className="contenedor">
      <h2>Solicitar matrícula</h2>

      {periodo && (
        <p>
          Periodo académico: <strong>{periodo.nombre}</strong> (asignado automáticamente)
        </p>
      )}

      {datosCursos && (
        <p>
          Semestre actual: <strong>{datosCursos.semestre_actual}</strong> — Créditos seleccionados:{" "}
          <strong>{creditosSeleccionados} / {creditosMaximos}</strong>
        </p>
      )}

      {error && <p style={{ color: "#ff6b6b" }}>{error}</p>}
      {mensaje && <p style={{ color: "#8fd18f" }}>{mensaje}</p>}

      {datosCursos && (
        <>
          {renderizarGrupo("Cursos de tu semestre", "regular")}
          {renderizarGrupo("Cursos desaprobados (para repetir)", "repetir")}
          {renderizarGrupo("Cursos de adelanto (siguiente semestre)", "adelanto")}

          <button type="button" onClick={manejarEnvio}>
            Enviar solicitud de matrícula
          </button>
        </>
      )}

      {ultimaMatriculaId && (
        <div style={{ marginTop: 16 }}>
          <button type="button" onClick={manejarDescargaFicha}>
            Descargar ficha (PDF)
          </button>
        </div>
      )}
    </div>
  );
}