import { useEffect, useState } from "react";
import { listarAuditorias, reportesEstrategicos } from "../../servicios/administracion.servicio";

export default function AdministracionAuditorias() {
  const [auditorias, setAuditorias] = useState([]);
  const [reportes, setReportes] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarDatos();
  }, []);

  async function cargarDatos() {
    const [resAuditorias, resReportes] = await Promise.all([
      listarAuditorias(),
      reportesEstrategicos(),
    ]);

    if (resAuditorias.error) {
      setError(resAuditorias.error);
      return;
    }

    if (!resReportes.error) {
      setReportes(resReportes.data);
    }

    setAuditorias(resAuditorias.data.registros ?? []);
  }

  return (
    <div className="contenedor">
      <h2>Auditorías y reportes</h2>
      <p></p>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {reportes && (
        <>
          <h3>Resumen estratégico</h3>
          <ul>
            <li>Estudiantes: {reportes.poblacion.total_estudiantes}</li>
            <li>Docentes: {reportes.poblacion.total_docentes}</li>
            <li>Matrículas: {reportes.matricula.total_solicitudes}</li>
            <li>Confirmadas: {reportes.matricula.confirmadas}</li>
            <li>Promedio institucional: {reportes.academico.promedio_institucional ?? "Sin datos"}</li>
            <li>Certificados emitidos: {reportes.certificados.emitidos}</li>
            <li>Certificados pendientes: {reportes.certificados.pendientes}</li>
          </ul>
        </>
      )}

      <h3>Auditorías</h3>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Usuario</th>
            <th>Acción</th>
            <th>Detalle</th>
            <th>Fecha</th>
          </tr>
        </thead>
        <tbody>
          {auditorias.map((auditoria) => (
            <tr key={auditoria.id}>
              <td>{auditoria.id}</td>
              <td>{auditoria.usuario_id}</td>
              <td>{auditoria.accion}</td>
              <td>{auditoria.detalle}</td>
              <td>{auditoria.created_at ? new Date(auditoria.created_at).toLocaleString() : "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}