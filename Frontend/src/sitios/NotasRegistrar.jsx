import { useEffect, useState } from "react";
import { misCursosAsignados } from "../servicios/cursosDocentes.servicio";
import { obtenerPlanilla, registrarNotasPlanilla, publicarNotas } from "../servicios/notas.servicio";

const TIPOS_NOTA = [
  { valor: "parcial1", etiqueta: "Parcial 1" },
  { valor: "parcial2", etiqueta: "Parcial 2" },
  { valor: "practica", etiqueta: "Práctica" },
  { valor: "final", etiqueta: "Final" },
];

const CAMPO_POR_TIPO = {
  parcial1: "nota_parcial1",
  parcial2: "nota_parcial2",
  practica: "nota_practica",
  final: "nota_final",
};

function valorValido(valor) {
  if (valor === "" || valor === null || valor === undefined) return true;
  const numero = Number(valor);
  return !Number.isNaN(numero) && numero >= 0 && numero <= 20;
}

export default function NotasRegistrar() {
  const [secciones, setSecciones] = useState([]);
  const [seccionId, setSeccionId] = useState("");
  const [tipoNota, setTipoNota] = useState("parcial1");
  const [planilla, setPlanilla] = useState(null);
  const [ediciones, setEdiciones] = useState({});
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);
  const [guardando, setGuardando] = useState(false);

  useEffect(() => {
    cargarSecciones();
  }, []);

  useEffect(() => {
    if (seccionId) cargarPlanilla();
  }, [seccionId]);

  async function cargarSecciones() {
    const { data, error } = await misCursosAsignados();
    if (!error) setSecciones(data);
  }

  async function cargarPlanilla() {
    setError(null);
    setMensaje(null);
    setEdiciones({});
    const { data, error } = await obtenerPlanilla(seccionId);
    if (error) {
      setError(error);
      setPlanilla(null);
      return;
    }
    setPlanilla(data);
  }

  function valorActual(estudiante) {
    if (ediciones[estudiante.estudiante_id] !== undefined) {
      return ediciones[estudiante.estudiante_id];
    }
    const campo = CAMPO_POR_TIPO[tipoNota];
    const valor = estudiante[campo];
    return valor === null || valor === undefined ? "" : String(valor);
  }

  function manejarCambio(estudianteId, valor) {
    setEdiciones((prev) => ({ ...prev, [estudianteId]: valor }));
  }

  const cronogramaVigente = planilla?.cronograma?.[tipoNota]?.vigente ?? true;
  const hayValoresInvalidos = planilla
    ? planilla.estudiantes.some((e) => !valorValido(valorActual(e)))
    : false;

  async function manejarGuardar() {
    if (!planilla) return;
    setMensaje(null);
    setError(null);

    const calificaciones = Object.entries(ediciones)
      .filter(([, valor]) => valor !== "")
      .map(([estudianteId, valor]) => ({
        estudiante_id: Number(estudianteId),
        calificacion: Number(valor),
      }));

    if (calificaciones.length === 0) {
      setError("No hay cambios para guardar");
      return;
    }

    setGuardando(true);
    const { data, error } = await registrarNotasPlanilla(seccionId, tipoNota, calificaciones);
    setGuardando(false);

    if (error) {
      setError(error);
      return;
    }

    setMensaje(data.mensaje);
    cargarPlanilla();
  }

  async function manejarPublicar() {
    setMensaje(null);
    setError(null);
    const { data, error } = await publicarNotas(seccionId);
    if (error) {
      setError(error);
      return;
    }
    setMensaje(data.mensaje);
  }

  return (
    <div className="contenedor">
      <h2>Planilla de Calificaciones</h2>

      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <select value={seccionId} onChange={(e) => setSeccionId(e.target.value)}>
          <option value="">Selecciona una sección</option>
          {secciones.map((s) => (
            <option key={s.oferta_academica_id} value={s.oferta_academica_id}>
              {s.nombre_curso}
            </option>
          ))}
        </select>

        <select value={tipoNota} onChange={(e) => setTipoNota(e.target.value)}>
          {TIPOS_NOTA.map((t) => (
            <option key={t.valor} value={t.valor}>
              {t.etiqueta}
            </option>
          ))}
        </select>
      </div>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {planilla && !cronogramaVigente && (
        <p style={{ color: "#ff6b6b" }}>Periodo de ingreso cerrado por la administración</p>
      )}

      {planilla && (
        <>
          <table>
            <thead>
              <tr>
                <th>Estudiante</th>
                <th>Parcial 1</th>
                <th>Parcial 2</th>
                <th>Práctica</th>
                <th>Final</th>
              </tr>
            </thead>
            <tbody>
              {planilla.estudiantes.map((estudiante) => {
                const valor = valorActual(estudiante);
                const invalido = !valorValido(valor);
                const bloqueado = !cronogramaVigente;

                return (
                  <tr key={estudiante.estudiante_id}>
                    <td>{estudiante.estudiante_nombre}</td>
                    <td>{tipoNota === "parcial1" ? "" : estudiante.nota_parcial1 ?? "-"}</td>
                    <td>{tipoNota === "parcial2" ? "" : estudiante.nota_parcial2 ?? "-"}</td>
                    <td>{tipoNota === "practica" ? "" : estudiante.nota_practica ?? "-"}</td>
                    <td>{tipoNota === "final" ? "" : estudiante.nota_final ?? "-"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          <h3>Editar {TIPOS_NOTA.find((t) => t.valor === tipoNota)?.etiqueta}</h3>
          <table>
            <thead>
              <tr>
                <th>Estudiante</th>
                <th>Calificación (0-20)</th>
              </tr>
            </thead>
            <tbody>
              {planilla.estudiantes.map((estudiante) => {
                const valor = valorActual(estudiante);
                const invalido = !valorValido(valor);
                const bloqueado = !cronogramaVigente;

                return (
                  <tr key={estudiante.estudiante_id}>
                    <td>{estudiante.estudiante_nombre}</td>
                    <td>
                      <input
                        type="text"
                        value={valor}
                        disabled={bloqueado}
                        onChange={(e) => manejarCambio(estudiante.estudiante_id, e.target.value)}
                        style={{
                          borderColor: invalido ? "#ff6b6b" : undefined,
                          borderWidth: invalido ? 2 : undefined,
                          backgroundColor: bloqueado ? "#333" : undefined,
                        }}
                      />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          <button
            type="button"
            onClick={manejarGuardar}
            disabled={guardando || hayValoresInvalidos || !cronogramaVigente}
          >
            {guardando ? "Guardando..." : "Guardar Cambios"}
          </button>
          <button type="button" onClick={manejarPublicar} style={{ marginLeft: 8 }}>
            Publicar notas a estudiantes
          </button>
        </>
      )}
    </div>
  );
}
