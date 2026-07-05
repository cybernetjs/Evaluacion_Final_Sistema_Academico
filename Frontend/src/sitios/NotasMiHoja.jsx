import { useEffect, useState } from "react";
import { miHojaDeNotas } from "../servicios/notas.servicio";

export default function NotasMiHoja() {
  const [semestreId, setSemestreId] = useState("");
  const [historial, setHistorial] = useState([]);
  const [progresoActual, setProgresoActual] = useState(null);
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    cargarHoja();
  }, []);

  async function cargarHoja(evento) {
    if (evento) {
      evento.preventDefault();
    }

    setError(null);
    setCargando(true);
    const { data, error } = await miHojaDeNotas(semestreId || null);
    setCargando(false);

    if (error) {
      setError(error);
      return;
    }

    const historialNormalizado = Array.isArray(data)
      ? data
      : Array.isArray(data?.historial)
        ? data.historial
        : [];

    setHistorial(historialNormalizado);
    setProgresoActual(Array.isArray(data) ? null : data?.progreso_actual ?? null);
  }

  return (
    <div className="contenedor">
      <h2>Mi hoja de notas</h2>
      <p>Consulta tus cursos, notas y progreso académico. Si dejas el semestre vacío, verás todo tu historial.</p>

      <form onSubmit={cargarHoja}>
        <div>
          <label>Filtrar por semestre</label>
          <input
            type="number"
            placeholder="Opcional"
            value={semestreId}
            onChange={(e) => setSemestreId(e.target.value)}
          />
        </div>
        <button type="submit">Consultar</button>
      </form>

      {cargando && <p>Cargando notas...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {!cargando && !error && (
        <>
          <h3>Progreso actual</h3>
          {progresoActual ? (
            <ul>
              <li>Créditos aprobados acumulados: {progresoActual.creditos_aprobados_acumulados}</li>
              <li>Promedio ponderado acumulado: {progresoActual.promedio_ponderado_acumulado}</li>
              <li>Estado de permanencia: {progresoActual.estado_permanencia_id}</li>
            </ul>
          ) : (
            <p>No hay progreso registrado para este estudiante.</p>
          )}

          <table>
            <thead>
              <tr>
                <th>Periodo</th>
                <th>Semestre</th>
                <th>Curso</th>
                <th>Promedio</th>
                <th>Créditos</th>
                <th>Orden de mérito</th>
              </tr>
            </thead>
            <tbody>
              {historial.length > 0 ? (
                historial.map((item, index) => (
                  <tr key={`${item.periodo_academico_id}-${index}`}>
                    <td>{item.periodo_academico_id}</td>
                    <td>{item.semestre_id}</td>
                    <td>{item.curso_nombre || "-"}</td>
                    <td>{item.promedio_ponderado_periodo}</td>
                    <td>{item.creditos_aprobados_periodo}</td>
                    <td>{item.orden_merito}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6">No hay registros de notas para mostrar.</td>
                </tr>
              )}
            </tbody>
          </table>
        </>
      )}

      {!cargando && !error && historial.length === 0 && !progresoActual && (
        <p>No se encontró información académica para este usuario. Si eres estudiante, revisa que tu cuenta tenga historial semilla cargado.</p>
      )}
    </div>
  );
}