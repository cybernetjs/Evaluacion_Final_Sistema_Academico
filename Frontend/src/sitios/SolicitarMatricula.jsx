import { useState, useEffect } from "react";
import {
  solicitarMatricula,
  obtenerPeriodoActual,
  obtenerCursosDisponibles,
  obtenerMiSolicitudActual,
  urlDescargarFichaPreliminar,
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
  const [cursoInfo, setCursoInfo] = useState(null);
  const [solicitudActual, setSolicitudActual] = useState(null);
  const [descargandoFicha, setDescargandoFicha] = useState(false);
  const [mostrarConfirmacion, setMostrarConfirmacion] = useState(false);

  useEffect(() => {
    cargarDatos();
  }, []);

  async function cargarDatos() {
    setCargando(true);
    const [resPeriodo, resCursos, resSolicitud] = await Promise.all([
      obtenerPeriodoActual(),
      obtenerCursosDisponibles(),
      obtenerMiSolicitudActual(),
    ]);

    if (!resPeriodo.error) setPeriodo(resPeriodo.data);
    if (!resCursos.error) setDatosCursos(resCursos.data);
    if (resCursos.error) setError(resCursos.error);
    if (!resSolicitud.error) setSolicitudActual(resSolicitud.data.matricula);

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

  function abrirConfirmacionEnvio() {
    setMensaje(null);
    setError(null);

    if (seleccionados.length === 0) {
      setError("Selecciona al menos un curso antes de enviar la solicitud");
      return;
    }

    setMostrarConfirmacion(true);
  }

  async function confirmarEnvio() {
    setMostrarConfirmacion(false);

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

  async function manejarDescargaFichaPreliminar() {
    if (descargandoFicha) return; 
    setDescargandoFicha(true);
    setError(null);

    try {
      const token = localStorage.getItem("token");
      const respuesta = await fetch(urlDescargarFichaPreliminar(), {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!respuesta.ok) {
        const cuerpo = await respuesta.json().catch(() => null);
        setError(cuerpo?.error || "No se pudo descargar la ficha preliminar");
        return;
      }

      const blob = await respuesta.blob();
      const url = window.URL.createObjectURL(blob);
      window.open(url, "_blank"); 
    } finally {
      setDescargandoFicha(false); 
    }
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
                  style={{
                    color: bloqueado ? "#ff6b6b" : undefined,
                    cursor: bloqueado ? "pointer" : undefined,
                  }}
                  onClick={() => {
                    if (bloqueado && !seleccionado) {
                      setCursoInfo({ nombre: curso.curso_nombre, motivo });
                    }
                  }}
                >                  <td>
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

          <button type="button" onClick={abrirConfirmacionEnvio}>
            Enviar solicitud de matrícula
          </button>
        </>
      )}


      {solicitudActual?.estado === "Pendiente" && (
        <div style={{ marginTop: 16 }}>
          <button type="button" onClick={manejarDescargaFichaPreliminar} disabled={descargandoFicha}>
            {descargandoFicha ? "Generando..." : "Descargar Ficha Preliminar"}
          </button>
        </div>
      )}

      {mostrarConfirmacion && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0,0,0,0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
          }}
          onClick={() => setMostrarConfirmacion(false)}
        >
          <div
            style={{
              background: "#1e1e1e",
              border: "1px solid #6b6bff",
              borderRadius: 8,
              padding: 20,
              maxWidth: 420,
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <p>
              ¿Está seguro de confirmar la matrícula? Esta acción cerrará el proceso de matrícula
              y no se permitirán modificaciones en las asignaturas. (Aún estarán permitidos la
              descarga de las fichas de matrícula preliminar y oficial)
            </p>
            <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
              <button type="button" onClick={confirmarEnvio}>
                Confirmar
              </button>
              <button type="button" onClick={() => setMostrarConfirmacion(false)}>
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}

      {cursoInfo && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0,0,0,0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
          }}
          onClick={() => setCursoInfo(null)}
        >
          <div
            style={{
              background: "#1e1e1e",
              border: "1px solid #ff6b6b",
              borderRadius: 8,
              padding: 20,
              maxWidth: 420,
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h4 style={{ color: "#ff6b6b", marginTop: 0 }}>⚠ {cursoInfo.nombre}</h4>
            <p>{cursoInfo.motivo}</p>
            <button type="button" onClick={() => setCursoInfo(null)}>
              Cerrar
            </button>
          </div>
        </div>
      )}
    </div>
  );
}