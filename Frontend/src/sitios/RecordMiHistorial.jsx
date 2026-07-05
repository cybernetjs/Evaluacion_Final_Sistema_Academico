import { useEffect, useState } from "react";
import { miHistorial } from "../servicios/recordAcademico.servicio";

export default function RecordMiHistorial() {
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarHistorial();
  }, []);

  async function cargarHistorial() {
    const { data, error } = await miHistorial();
    if (error) {
      setError(error);
      return;
    }

    setDatos(data);
  }

  return (
    <div className="contenedor">
      <h2>Mi historial académico</h2>
      <p>Revisa tu historial completo y tu progreso actual.</p>

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
            <p>No se encontró progreso registrado.</p>
          )}

          <table>
            <thead>
              <tr>
                <th>Periodo</th>
                <th>Semestre</th>
                <th>Promedio</th>
                <th>Créditos</th>
                <th>Orden</th>
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