import { useEffect, useState } from "react";
import { desempenoPorCohorte, reportesConsolidados } from "../servicios/recordAcademico.servicio";

export default function RecordReportes() {
  const [resumen, setResumen] = useState(null);
  const [cohortes, setCohortes] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarDatos();
  }, []);

  async function cargarDatos() {
    const [resResumen, resCohortes] = await Promise.all([
      reportesConsolidados(),
      desempenoPorCohorte(),
    ]);

    if (resResumen.error) {
      setError(resResumen.error);
      return;
    }

    if (!resCohortes.error) {
      setCohortes(resCohortes.data);
    }

    setResumen(resResumen.data);
  }

  return (
    <div className="contenedor">
      <h2>Reportes académicos</h2>
      <p>Consolida el estado institucional y el desempeño por cohorte.</p>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {resumen && (
        <>
          <h3>Resumen general</h3>
          <ul>
            <li>Total de estudiantes: {resumen.total_estudiantes}</li>
            <li>Estudiantes con progreso: {resumen.estudiantes_con_registro_de_progreso}</li>
            <li>Promedio institucional: {resumen.promedio_general_institucional ?? "Sin datos"}</li>
          </ul>
        </>
      )}

      <h3>Desempeño por cohorte</h3>
      <table>
        <thead>
          <tr>
            <th>Especialidad</th>
            <th>Total estudiantes</th>
            <th>Promedio ponderado</th>
          </tr>
        </thead>
        <tbody>
          {cohortes.map((item) => (
            <tr key={item.especialidad_id}>
              <td>{item.especialidad_id}</td>
              <td>{item.total_estudiantes}</td>
              <td>{item.promedio_ponderado}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}