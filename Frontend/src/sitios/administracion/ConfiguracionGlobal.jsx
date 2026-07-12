import { useEffect, useState } from "react";
import {
  obtenerConfiguracionCiclo,
  actualizarConfiguracionCiclo,
  listarPeriodos,
} from "../../servicios/administracion.servicio";

const MODULOS_AFECTADOS_POR_ESTADO = {
  "Planificacion Horaria": ["Matrícula", "Registro de notas", "Cierre de actas"],
  "Inscripcion de Matricula Abierta": ["Registro de notas", "Cierre de actas"],
  "Periodo de Clases Regular": ["Matrícula", "Cierre de actas"],
  "Registro de Notas Parciales": ["Matrícula"],
  "Cierre de Actas": ["Matrícula", "Registro de notas"],
  "Inactivo/Historico": ["Matrícula", "Registro de notas", "Cierre de actas"],
};

function aFechaLocal(valorIso) {
  if (!valorIso) return "";
  return valorIso.slice(0, 16);
}

export default function ConfiguracionGlobal() {
  const [periodos, setPeriodos] = useState([]);
  const [configuracion, setConfiguracion] = useState(null);
  const [formulario, setFormulario] = useState({
    periodo_academico_id: "",
    estado_ciclo: "",
    fecha_cierre_matricula: "",
    fecha_limite_notas: "",
    fecha_cierre_actas: "",
  });
  const [mostrarAdvertencia, setMostrarAdvertencia] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarDatos();
  }, []);

  async function cargarDatos() {
    const [resConfig, resPeriodos] = await Promise.all([
      obtenerConfiguracionCiclo(),
      listarPeriodos(),
    ]);

    if (!resPeriodos.error) setPeriodos(resPeriodos.data);

    if (!resConfig.error) {
      setConfiguracion(resConfig.data);
      setFormulario({
        periodo_academico_id: resConfig.data.periodo_academico_id || "",
        estado_ciclo: resConfig.data.estado_ciclo,
        fecha_cierre_matricula: aFechaLocal(resConfig.data.fecha_cierre_matricula),
        fecha_limite_notas: aFechaLocal(resConfig.data.fecha_limite_notas),
        fecha_cierre_actas: aFechaLocal(resConfig.data.fecha_cierre_actas),
      });
    }
  }

  function actualizarCampo(campo, valor) {
    setFormulario((f) => ({ ...f, [campo]: valor }));
  }

  const fechasEnOrden =
    (!formulario.fecha_cierre_matricula || !formulario.fecha_limite_notas || formulario.fecha_limite_notas >= formulario.fecha_cierre_matricula) &&
    (!formulario.fecha_limite_notas || !formulario.fecha_cierre_actas || formulario.fecha_cierre_actas >= formulario.fecha_limite_notas);

  async function confirmarGuardado() {
    setMostrarAdvertencia(false);
    setGuardando(true);
    setMensaje(null);
    setError(null);

    const { data, error } = await actualizarConfiguracionCiclo({
      periodo_academico_id: formulario.periodo_academico_id || null,
      estado_ciclo: formulario.estado_ciclo,
      fecha_cierre_matricula: formulario.fecha_cierre_matricula || null,
      fecha_limite_notas: formulario.fecha_limite_notas || null,
      fecha_cierre_actas: formulario.fecha_cierre_actas || null,
    });

    setGuardando(false);

    if (error) {
      setError(error);
      return;
    }

    setMensaje(data.mensaje);
    cargarDatos();
  }

  if (!configuracion) {
    return <div className="contenedor"><p>Cargando configuración...</p></div>;
  }

  const modulosAfectados = MODULOS_AFECTADOS_POR_ESTADO[formulario.estado_ciclo] || [];

  return (
    <div className="contenedor">
      <h2>Configuración del ciclo académico</h2>
      <p>Panel exclusivo del Administrador para controlar el estado general del periodo lectivo vigente.</p>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {!fechasEnOrden && (
        <p style={{ color: "red" }}>
          Las fechas hito deben mantener el orden: cierre de matrícula, límite de notas y cierre de actas.
        </p>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 16, maxWidth: 480 }}>
        <div>
          <label>Periodo académico vigente</label>
          <select
            value={formulario.periodo_academico_id}
            onChange={(e) => actualizarCampo("periodo_academico_id", e.target.value)}
          >
            <option value="">Sin periodo asignado</option>
            {periodos.map((p) => (
              <option key={p.id} value={p.id}>{p.nombre}</option>
            ))}
          </select>
        </div>

        <div>
          <label>Estado del ciclo</label>
          <select
            value={formulario.estado_ciclo}
            onChange={(e) => actualizarCampo("estado_ciclo", e.target.value)}
          >
            {configuracion.estados_disponibles.map((estado) => (
              <option key={estado} value={estado}>{estado}</option>
            ))}
          </select>
        </div>

        <div>
          <label>Fecha de cierre de matrícula regular</label>
          <input
            type="datetime-local"
            value={formulario.fecha_cierre_matricula}
            onChange={(e) => actualizarCampo("fecha_cierre_matricula", e.target.value)}
          />
        </div>

        <div>
          <label>Fecha límite de registro de notas</label>
          <input
            type="datetime-local"
            value={formulario.fecha_limite_notas}
            onChange={(e) => actualizarCampo("fecha_limite_notas", e.target.value)}
          />
        </div>

        <div>
          <label>Fecha de cierre de actas consolidadas</label>
          <input
            type="datetime-local"
            value={formulario.fecha_cierre_actas}
            onChange={(e) => actualizarCampo("fecha_cierre_actas", e.target.value)}
          />
        </div>

        <button
          type="button"
          disabled={!fechasEnOrden || guardando}
          onClick={() => setMostrarAdvertencia(true)}
        >
          {guardando ? "Guardando..." : "Guardar configuración"}
        </button>
      </div>

      {mostrarAdvertencia && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0,0,0,0.6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1100,
          }}
          onClick={() => setMostrarAdvertencia(false)}
        >
          <div
            style={{ background: "#1e1e1e", border: "1px solid #f2c14e", borderRadius: 8, padding: 20, maxWidth: 460 }}
            onClick={(e) => e.stopPropagation()}
          >
            <h4 style={{ marginTop: 0 }}>Advertencia de impacto</h4>
            <p>
              Cambiar el estado del ciclo a <strong>{formulario.estado_ciclo}</strong> deshabilitará
              automáticamente para los usuarios externos:
            </p>
            {modulosAfectados.length > 0 ? (
              <ul>
                {modulosAfectados.map((modulo) => (
                  <li key={modulo}>{modulo}</li>
                ))}
              </ul>
            ) : (
              <p>Ningún módulo adicional se verá restringido con este estado.</p>
            )}
            <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
              <button type="button" onClick={confirmarGuardado}>Confirmar cambio</button>
              <button type="button" onClick={() => setMostrarAdvertencia(false)}>Cancelar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
