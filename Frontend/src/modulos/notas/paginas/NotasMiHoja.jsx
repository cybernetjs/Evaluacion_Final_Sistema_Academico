import { useEffect, useState } from "react";
import { obtenerCiclosCursados, obtenerHojaCiclo } from "../servicios/notasServicio";

function celda(valor) {
  return valor === null || valor === undefined ? "Pendiente" : valor;
}

export default function NotasMiHoja() {
  const [ciclos, setCiclos] = useState([]);
  const [periodoId, setPeriodoId] = useState("");
  const [cursos, setCursos] = useState([]);
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    cargarCiclos();
  }, []);

  useEffect(() => {
    cargarHoja();
  }, [periodoId]);

  async function cargarCiclos() {
    const { data, error } = await obtenerCiclosCursados();
    if (!error) setCiclos(data);
  }

  async function cargarHoja() {
    setCargando(true);
    setError(null);
    const { data, error } = await obtenerHojaCiclo(periodoId || null);
    setCargando(false);

    if (error) {
      setError(error);
      return;
    }
    setCursos(data);
  }

  const cicloSeleccionado = ciclos.find((c) => String(c.periodo_academico_id) === String(periodoId));
  const esHistorico = periodoId && cicloSeleccionado;

  return (
    <div className="contenedor">
      <h2>Hoja de Notas</h2>

      <div style={{ marginBottom: 16 }}>
        <label>Ciclo académico</label>
        <select value={periodoId} onChange={(e) => setPeriodoId(e.target.value)}>
          <option value="">Ciclo activo</option>
          {ciclos.map((c) => (
            <option key={c.periodo_academico_id} value={c.periodo_academico_id}>
              {c.nombre}
            </option>
          ))}
        </select>
      </div>

      {esHistorico && <p style={{ opacity: 0.7 }}>Consultando historial </p>}

      {error && <p style={{ color: "red" }}>{error}</p>}
      {cargando && <p>Cargando...</p>}

      {!cargando && !error && (
        <table>
          <thead>
            <tr>
              <th>Curso</th>
              <th>Parcial 1</th>
              <th>Parcial 2</th>
              <th>Práctica</th>
              <th>Promedio Final</th>
            </tr>
          </thead>
          <tbody>
            {cursos.length > 0 ? (
              cursos.map((c, index) => (
                <tr key={`${c.curso_id}-${index}`}>
                  <td>{c.curso_nombre}</td>
                  <td>{celda(c.nota_parcial1)}</td>
                  <td>{celda(c.nota_parcial2)}</td>
                  <td>{celda(c.nota_practica)}</td>
                  <td style={{ fontWeight: "bold" }}>{celda(c.nota_final)}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="5">No hay cursos matriculados en este ciclo.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}
