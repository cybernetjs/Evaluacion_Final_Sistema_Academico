import { useState, useEffect } from "react";
import { obtenerEstadisticas } from "../servicios/matricula.servicio";

export default function EstadisticasMatricula() {
  const [estadisticas, setEstadisticas] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarEstadisticas();
  }, []);

  async function cargarEstadisticas() {
    const { data, error } = await obtenerEstadisticas();
    if (error) {
      setError(error);
      return;
    }
    setEstadisticas(data);
  }

  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (!estadisticas) return <p>Cargando...</p>;

  return (
    <div>
      <h2>Estadísticas de matrícula</h2>
      <ul>
        <li>Total de solicitudes: {estadisticas.total_solicitudes}</li>
        <li>Matriculados: {estadisticas.matriculados}</li>
        <li>Pendientes: {estadisticas.pendientes}</li>
        <li>Validados: {estadisticas.validados}</li>
      </ul>
    </div>
  );
}