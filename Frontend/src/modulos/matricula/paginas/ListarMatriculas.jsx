import { useState, useEffect } from "react";
import {
  listarMatriculas,
  listarEstadosMatricula,
  validarRequisitos,
  generarFichaOficial,
  cancelarMatricula,
  obtenerComprobanteMatriculaBlobUrl,
} from "../servicios/matriculaServicio";
import { listarEspecialidades } from "../../administracion/servicios/administracionServicio";
import { listarPeriodos } from "../servicios/matriculaServicio";
import ModalVerificarPago from "../componentes/ModalVerificarPago";

export default function ListarMatriculas() {
  const [matriculas, setMatriculas] = useState([]);
  const [total, setTotal] = useState(0);
  const [estados, setEstados] = useState([]);
  const [especialidades, setEspecialidades] = useState([]);
  const [periodos, setPeriodos] = useState([]);
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [filtros, setFiltros] = useState({ periodoId: "", especialidadId: "", estado: "" });
  const [pagina, setPagina] = useState(1);
  const porPagina = 10;
  const [matriculaACancelar, setMatriculaACancelar] = useState(null);
  const [matriculaAVerificar, setMatriculaAVerificar] = useState(null);
  const [comprobanteUrl, setComprobanteUrl] = useState(null);
  const [cargandoComprobante, setCargandoComprobante] = useState(false);

  useEffect(() => {
    cargarCatalogos();
  }, []);

  useEffect(() => {
    cargarMatriculas();
  }, [filtros, pagina]);

  async function cargarCatalogos() {
    const [resEstados, resEspecialidades, resPeriodos] = await Promise.all([
      listarEstadosMatricula(),
      listarEspecialidades(),
      listarPeriodos(),
    ]);
    if (!resEstados.error) setEstados(resEstados.data);
    if (!resEspecialidades.error) setEspecialidades(resEspecialidades.data);
    if (!resPeriodos.error) setPeriodos(resPeriodos.data);
  }

  async function cargarMatriculas() {
    setCargando(true);
    const { data, error } = await listarMatriculas({ ...filtros, pagina, porPagina });
    setCargando(false);

    if (error) return setError(error);
    setMatriculas(data.matriculas);
    setTotal(data.total);
  }

  function actualizarFiltro(campo, valor) {
    setPagina(1);
    setFiltros((f) => ({ ...f, [campo]: valor }));
  }

  function puedeValidar(matricula) {
    return matricula.estado === "Pendiente";
  }

  function puedeVerificarPago(matricula) {
    return matricula.estado === "Validado" && !matricula.pagado && matricula.tiene_comprobante;
  }

  function puedeGenerarFicha(matricula) {
    return matricula.estado === "Validado" && matricula.pagado === true;
  }

  function puedeDescargarFichaOficial(matricula) {
    return matricula.estado === "Matriculado";
  }

  async function manejarValidar(id) {
    setMensaje(null);
    setError(null);
    const { data, error } = await validarRequisitos(id);
    if (error) return setError(error);
    setMensaje(data.mensaje);
    cargarMatriculas();
  }

  async function abrirVerificacionPago(matricula) {
    setMatriculaAVerificar(matricula);
    setComprobanteUrl(null);
    setCargandoComprobante(true);
    const { data, error } = await obtenerComprobanteMatriculaBlobUrl(matricula.id);
    setCargandoComprobante(false);
    if (error) {
      setError(error);
      return;
    }
    setComprobanteUrl(data);
  }

  function cerrarVerificacionPago() {
    setComprobanteUrl((actual) => {
      if (actual) URL.revokeObjectURL(actual);
      return null;
    });
    setMatriculaAVerificar(null);
  }

  function manejarExitoVerificacion(data) {
    setMensaje(data.mensaje);
    cerrarVerificacionPago();
    cargarMatriculas();
  }

  async function manejarFicha(id) {
    setMensaje(null);
    setError(null);
    const { data, error } = await generarFichaOficial(id);
    if (error) return setError(error);
    setMensaje(data.mensaje);
    cargarMatriculas();
  }

  async function manejarDescargaFichaOficial(id) {
    setError(null);
    const token = localStorage.getItem("token");
    const respuesta = await fetch(`https://sistema-academico-backend-wfcn.onrender.com/api/matriculas/${id}/ficha`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!respuesta.ok) {
      const cuerpo = await respuesta.json().catch(() => null);
      setError(cuerpo?.error || "No se pudo descargar la ficha oficial");
      return;
    }

    const blob = await respuesta.blob();
    const url = window.URL.createObjectURL(blob);
    window.open(url, "_blank");
  }

  async function confirmarCancelacion() {
    setMensaje(null);
    setError(null);
    const { data, error } = await cancelarMatricula(matriculaACancelar.id);
    setMatriculaACancelar(null);
    if (error) return setError(error);
    setMensaje(`Matrícula ${data.id} cancelada correctamente`);
    cargarMatriculas();
  }

  const totalPaginas = Math.max(1, Math.ceil(total / porPagina));

  return (
    <div className="contenedor">
      <h2>Bandeja de Validación de Matrículas</h2>

      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <select value={filtros.periodoId} onChange={(e) => actualizarFiltro("periodoId", e.target.value)}>
          <option value="">Todos los ciclos</option>
          {periodos.map((p) => (
            <option key={p.id} value={p.id}>
              {p.nombre}
            </option>
          ))}
        </select>

        <select value={filtros.especialidadId} onChange={(e) => actualizarFiltro("especialidadId", e.target.value)}>
          <option value="">Todas las especialidades</option>
          {especialidades.map((e) => (
            <option key={e.id} value={e.id}>
              {e.nombre}
            </option>
          ))}
        </select>

        <select value={filtros.estado} onChange={(e) => actualizarFiltro("estado", e.target.value)}>
          <option value="">Todos los estados</option>
          {estados.map((e) => (
            <option key={e.id} value={e.nombre}>
              {e.nombre}
            </option>
          ))}
        </select>
      </div>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {cargando ? (
        <p>Cargando matrículas...</p>
      ) : (
        <>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Estudiante</th>
                <th>Especialidad</th>
                <th>Ciclo</th>
                <th>Estado</th>
                <th>Pagado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {matriculas.length > 0 ? (
                matriculas.map((m) => (
                  <tr key={m.id}>
                    <td>{m.id}</td>
                    <td>{m.estudiante_nombre}</td>
                    <td>{m.especialidad_nombre}</td>
                    <td>{m.periodo_nombre}</td>
                    <td>{m.estado}</td>
                    <td>{m.pagado ? "Sí" : "No"}</td>
                    <td>
                      <button type="button" onClick={() => manejarValidar(m.id)} disabled={!puedeValidar(m)}>
                        Validar
                      </button>
                      <button
                        type="button"
                        onClick={() => abrirVerificacionPago(m)}
                        disabled={!puedeVerificarPago(m)}
                        title={
                          !m.tiene_comprobante
                            ? "El estudiante todavía no envió el comprobante"
                            : m.pagado
                            ? "El pago ya fue verificado"
                            : undefined
                        }
                      >
                        Verificar pago
                      </button>
                      <button type="button" onClick={() => manejarFicha(m.id)} disabled={!puedeGenerarFicha(m)}>
                        Generar ficha oficial
                      </button>
                      <button
                        type="button"
                        onClick={() => manejarDescargaFichaOficial(m.id)}
                        disabled={!puedeDescargarFichaOficial(m)}
                      >
                        Descargar ficha oficial
                      </button>
                      <button
                        type="button"
                        onClick={() => setMatriculaACancelar(m)}
                        disabled={!m.puede_cancelar}
                        title={!m.puede_cancelar ? "Solo disponible si el plazo de pago venció" : undefined}
                      >
                        Observar/Cancelar Matrícula
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7">No hay matrículas registradas.</td>
                </tr>
              )}
            </tbody>
          </table>

          <div style={{ display: "flex", gap: 8, marginTop: 12, alignItems: "center" }}>
            <button type="button" onClick={() => setPagina((p) => Math.max(1, p - 1))} disabled={pagina <= 1}>
              Anterior
            </button>
            <span>
              Página {pagina} de {totalPaginas}
            </span>
            <button
              type="button"
              onClick={() => setPagina((p) => Math.min(totalPaginas, p + 1))}
              disabled={pagina >= totalPaginas}
            >
              Siguiente
            </button>
          </div>
        </>
      )}

      {matriculaACancelar && (
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
          onClick={() => setMatriculaACancelar(null)}
        >
          <div
            style={{ background: "#1e1e1e", border: "1px solid #ff6b6b", borderRadius: 8, padding: 20, maxWidth: 420 }}
            onClick={(e) => e.stopPropagation()}
          >
            <h4 style={{ marginTop: 0 }}>Cancelar matrícula #{matriculaACancelar.id}</h4>
            <label>Motivo de observación</label>
            <input
              type="text"
              readOnly
              value="Cancelación por incumplimiento del periodo de pago establecido"
              style={{ width: "100%", marginTop: 4, marginBottom: 12 }}
            />
            <div style={{ display: "flex", gap: 8 }}>
              <button type="button" onClick={confirmarCancelacion}>
                Confirmar cancelación
              </button>
              <button type="button" onClick={() => setMatriculaACancelar(null)}>
                Volver
              </button>
            </div>
          </div>
        </div>
      )}

      {matriculaAVerificar && (
        <ModalVerificarPago
          matricula={matriculaAVerificar}
          comprobanteUrl={comprobanteUrl}
          cargandoComprobante={cargandoComprobante}
          onCerrar={cerrarVerificacionPago}
          onExito={manejarExitoVerificacion}
        />
      )}
    </div>
  );
}
