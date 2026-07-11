import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import {
  indicadoresAcademicos,
  listarNotas,
  obtenerNotasMatricula,
  panelActas,
  alumnosOmisos,
  cerrarActa,
  estadoPeriodoConsolidacion,
  consolidarSemestre,
} from "../servicios/notas.servicio";
import { listarPeriodos } from "../servicios/matricula.servicio";

export default function NotasGestion() {
  const { usuario } = useAuth();
  const [notas, setNotas] = useState([]);
  const [matriculaId, setMatriculaId] = useState("");
  const [consulta, setConsulta] = useState([]);
  const [actas, setActas] = useState([]);
  const [omisosPorOferta, setOmisosPorOferta] = useState({});
  const [actaAConfirmar, setActaAConfirmar] = useState(null);
  const [periodos, setPeriodos] = useState([]);
  const [periodoSeleccionado, setPeriodoSeleccionado] = useState("");
  const [estadoConsolidacion, setEstadoConsolidacion] = useState(null);
  const [consolidando, setConsolidando] = useState(false);
  const [resultadoConsolidacion, setResultadoConsolidacion] = useState(null);
  const [indicadores, setIndicadores] = useState(null);
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    function confirmarSalida(evento) {
      if (consolidando) {
        evento.preventDefault();
        evento.returnValue = "";
      }
    }
    window.addEventListener("beforeunload", confirmarSalida);
    return () => window.removeEventListener("beforeunload", confirmarSalida);
  }, [consolidando]);

  useEffect(() => {
    cargarNotas();
    if (usuario?.rol === "administrador") {
      cargarActas();
      cargarPeriodos();
    }
  }, [usuario]);

  useEffect(() => {
    if (periodoSeleccionado) cargarEstadoConsolidacion();
  }, [periodoSeleccionado]);

  async function cargarPeriodos() {
    const { data, error } = await listarPeriodos();
    if (!error) setPeriodos(data);
  }

  async function cargarEstadoConsolidacion() {
    const { data, error } = await estadoPeriodoConsolidacion(periodoSeleccionado);
    if (!error) setEstadoConsolidacion(data);
  }

  async function manejarConsolidar() {
    setConsolidando(true);
    setResultadoConsolidacion(null);
    setError(null);

    const { data, error } = await consolidarSemestre(periodoSeleccionado);
    setConsolidando(false);

    if (error) {
      setError(error);
      return;
    }

    setResultadoConsolidacion(data);
    cargarEstadoConsolidacion();
  }

  async function cargarNotas() {
    const { data, error } = await listarNotas();
    if (!error) {
      setNotas(data);
    }
  }

  async function cargarActas() {
    const { data, error } = await panelActas();
    if (!error) setActas(data);
  }

  async function manejarConsulta(evento) {
    evento.preventDefault();
    setMensaje(null);
    setError(null);

    const { data, error } = await obtenerNotasMatricula(matriculaId);

    if (error) {
      setError(error);
      return;
    }

    setConsulta(data);
  }

  async function manejarVerOmisos(ofertaAcademicaId) {
    const { data, error } = await alumnosOmisos(ofertaAcademicaId);
    if (error) return;
    setOmisosPorOferta((prev) => ({ ...prev, [ofertaAcademicaId]: data }));
  }

  async function confirmarCierreActa() {
    setMensaje(null);
    setError(null);
    const oferta = actaAConfirmar;
    setActaAConfirmar(null);

    const { data, error } = await cerrarActa(oferta.oferta_academica_id);

    if (error) {
      setError(error);
      return;
    }

    setMensaje(`${data.mensaje}. Hash de auditoría: ${data.hash_auditoria}`);
    cargarActas();
  }

  async function manejarIndicadores() {
    setMensaje(null);
    setError(null);
    const { data, error } = await indicadoresAcademicos();

    if (error) {
      setError(error);
      return;
    }

    setIndicadores(data);
  }

  return (
    <div className="contenedor">
      <h2>Gestión de notas</h2>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {usuario?.rol === "administrador" && (
        <>
          <h3>Panel de Control de Actas por Sección</h3>
          <table>
            <thead>
              <tr>
                <th>Código</th>
                <th>Sección</th>
                <th>Docente</th>
                <th>% Notas Ingresadas</th>
                <th>Estado del Acta</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {actas.map((a) => (
                <tr key={a.oferta_academica_id}>
                  <td>{a.curso_codigo}</td>
                  <td>{a.oferta_academica_id}</td>
                  <td>{a.docente ?? "Sin asignar"}</td>
                  <td>{a.porcentaje_notas_ingresadas}%</td>
                  <td>{a.estado_acta === "Cerrada" ? "Cerrada/Consolidada" : "Abierta"}</td>
                  <td>
                    <button
                      type="button"
                      onClick={() => setActaAConfirmar(a)}
                      disabled={!a.puede_cerrar}
                      title={!a.puede_cerrar ? "Solo disponible con el 100% de notas ingresadas" : undefined}
                    >
                      Validar y Cerrar Acta
                    </button>
                    {a.porcentaje_notas_ingresadas < 100 && a.estado_acta !== "Cerrada" && (
                      <button type="button" onClick={() => manejarVerOmisos(a.oferta_academica_id)}>
                        Ver alumnos pendientes
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {Object.entries(omisosPorOferta).map(([ofertaId, omisos]) => (
            <div key={ofertaId} style={{ marginTop: 12 }}>
              <p>Alumnos sin nota final en la sección {ofertaId}:</p>
              <ul>
                {omisos.map((o) => (
                  <li key={o.estudiante_id}>{o.estudiante_nombre}</li>
                ))}
              </ul>
            </div>
          ))}

          <h3 style={{ marginTop: 32 }}>Cierre y Consolidación Semestral</h3>
          <select value={periodoSeleccionado} onChange={(e) => setPeriodoSeleccionado(e.target.value)}>
            <option value="">Selecciona un periodo</option>
            {periodos.map((p) => (
              <option key={p.id} value={p.id}>
                {p.nombre}
              </option>
            ))}
          </select>

          {estadoConsolidacion && (
            <div style={{ marginTop: 12 }}>
              <p>
                Actas cerradas: {estadoConsolidacion.actas_cerradas} / {estadoConsolidacion.total_actas}
              </p>

              {!estadoConsolidacion.todas_cerradas && estadoConsolidacion.secciones_pendientes.length > 0 && (
                <div>
                  <p style={{ color: "#ff6b6b" }}>Secciones con actas abiertas (bloquean la consolidación):</p>
                  <ul>
                    {estadoConsolidacion.secciones_pendientes.map((s) => (
                      <li key={s.oferta_academica_id}>
                        {s.curso_codigo} — {s.curso_nombre}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <button
                type="button"
                onClick={manejarConsolidar}
                disabled={!estadoConsolidacion.todas_cerradas || consolidando}
              >
                Ejecutar Consolidación Semestral
              </button>

              {consolidando && (
                <div style={{ marginTop: 8 }}>
                  <div style={{ width: "100%", background: "#333", borderRadius: 4, overflow: "hidden" }}>
                    <div style={{ width: "60%", background: "#6b6bff", height: 10 }} />
                  </div>
                  <p>Procesando expedientes, no cierres ni recargues esta página...</p>
                </div>
              )}

              {resultadoConsolidacion && (
                <div style={{ marginTop: 12 }}>
                  <p style={{ color: "green" }}>
                    Expedientes actualizados con éxito: {resultadoConsolidacion.total_expedientes_actualizados}
                  </p>
                  {resultadoConsolidacion.errores.length > 0 && (
                    <>
                      <p style={{ color: "#ff6b6b" }}>Errores de cómputo:</p>
                      <table>
                        <thead>
                          <tr>
                            <th>Estudiante</th>
                            <th>Código de error</th>
                            <th>Detalle</th>
                          </tr>
                        </thead>
                        <tbody>
                          {resultadoConsolidacion.errores.map((e, i) => (
                            <tr key={i}>
                              <td>{e.estudiante_id}</td>
                              <td>{e.codigo_error}</td>
                              <td>{e.detalle}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </>
                  )}
                </div>
              )}
            </div>
          )}
        </>
      )}

      {(usuario?.rol === "administrador" || usuario?.rol === "direccion") && (
        <div style={{ marginTop: 16 }}>
          <button type="button" onClick={manejarIndicadores}>
            Ver indicadores
          </button>
        </div>
      )}

      {indicadores && (
        <ul>
          <li>Promedio general: {indicadores.promedio_general ?? "Sin datos"}</li>
          <li>Total evaluados: {indicadores.total_evaluados}</li>
        </ul>
      )}

      {actaAConfirmar && (
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
          onClick={() => setActaAConfirmar(null)}
        >
          <div
            style={{ background: "#1e1e1e", border: "1px solid #ff6b6b", borderRadius: 8, padding: 20, maxWidth: 420 }}
            onClick={(e) => e.stopPropagation()}
          >
            <p>
              ¿Está seguro de cerrar formalmente el acta de la sección {actaAConfirmar.curso_codigo}?
            </p>
            <div style={{ display: "flex", gap: 8 }}>
              <button type="button" onClick={confirmarCierreActa}>
                Confirmar cierre
              </button>
              <button type="button" onClick={() => setActaAConfirmar(null)}>
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}

      <h3>Consolidado general</h3>
      <table>
        <thead>
          <tr>
            <th>Matrícula</th>
            <th>Oferta</th>
            <th>Parcial</th>
            <th>Final</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {notas.map((nota) => (
            <tr key={`${nota.matricula_id}-${nota.oferta_academica_id}`}>
              <td>{nota.matricula_id}</td>
              <td>{nota.oferta_academica_id}</td>
              <td>{nota.nota_parcial ?? "-"}</td>
              <td>{nota.nota_final ?? "-"}</td>
              <td>{nota.estado_curso}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Consulta por matrícula</h3>
      <form onSubmit={manejarConsulta}>
        <label>ID de matrícula</label>
        <input type="number" value={matriculaId} onChange={(e) => setMatriculaId(e.target.value)} required />
        <button type="submit">Consultar matrícula</button>
      </form>
      <table>
        <thead>
          <tr>
            <th>Oferta</th>
            <th>Parcial</th>
            <th>Final</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {consulta.map((nota, index) => (
            <tr key={`${nota.oferta_academica_id}-${index}`}>
              <td>{nota.oferta_academica_id}</td>
              <td>{nota.nota_parcial ?? "-"}</td>
              <td>{nota.nota_final ?? "-"}</td>
              <td>{nota.estado_curso}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
