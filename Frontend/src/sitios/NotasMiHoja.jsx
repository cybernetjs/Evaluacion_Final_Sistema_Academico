import { useEffect, useState } from "react";
import { miHojaDeNotas } from "../servicios/notas.servicio";

export default function NotasMiHoja() {
  const [semestreId, setSemestreId] = useState("");
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarHoja();
  }, []);

  async function cargarHoja(evento) {
    if (evento) {
      evento.preventDefault();
    }

    setError(null);
    const { data, error } = await miHojaDeNotas(semestreId || null);

    if (error) {
      setError(error);
      return;
    }

    setDatos(data);
  }

  return (
    <div className="contenedor">
      <h2>Mi hoja de notas</h2>
      <p>Consulta tu historial académico por ciclo o semestre.</p>

      <form onSubmit={cargarHoja}>
        <div>
          <label>Semestre opcional</label>
          <input
            type="number"
            value={semestreId}
            onChange={(e) => setSemestreId(e.target.value)}
          />
        </div>
        <button type="submit">Consultar</button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {datos && (
        <>
          <h3>Progreso actual</h3>
          {datos.progreso_actual ? (
            <ul>
              <li>Créditos aprobados acumulados: {datos.progreso_actual.creditos_aprobados_acumulados}</li>
              <li>Promedio ponderado acumulado: {datos.progreso_actual.promedio_ponderado_acumulado}</li>
              <li>Estado de permanencia: {datos.progreso_actual.estado_permanencia_id}</li>
            </ul>
          ) : (
            <p>No hay progreso registrado.</p>
          )}

          <table>
            <thead>
              <tr>
                <th>Periodo</th>
                <th>Semestre</th>
                <th>Promedio</th>
                <th>Créditos</th>
                <th>Orden de mérito</th>
              </tr>
            </thead>
            <tbody>
              {datos.historial.map((item, index) => (
                <tr key={`${item.periodo_academico_id}-${index}`}>
                  <td>{item.periodo_academico_id}</td>
                  <td>{item.semestre_id}</td>
                  <td>{item.promedio_ponderado_periodo}</td>
                  <td>{item.creditos_aprobados_periodo}</td>
                  <td>{item.orden_merito}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}