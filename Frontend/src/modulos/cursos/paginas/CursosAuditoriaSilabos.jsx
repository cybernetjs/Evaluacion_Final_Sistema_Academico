import { useEffect, useState } from "react";
import { cumplimientoSilabos } from "../servicios/cursosServicio";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";

export default function CursosAuditoriaSilabos() {
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarDatos();
  }, []);

  async function cargarDatos() {
    const { data, error } = await cumplimientoSilabos();
    if (error) {
      setError(error);
      return;
    }
    setError(null);
    setDatos(data);
  }

  return (
    <div className="contenedor">
      <h2>Auditoría de cumplimiento de sílabos</h2>
      <p>Estado de avance de la carga de sílabos para el periodo académico vigente.</p>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {datos && (
        <>
          <div style={{ display: "flex", gap: 16, marginBottom: 24 }}>
            <div style={{ border: "1px solid #444", borderRadius: 8, padding: 16, minWidth: 200 }}>
              <p style={{ margin: 0, opacity: 0.7 }}>Porcentaje general cargado</p>
              <p style={{ margin: 0, fontSize: 28, fontWeight: "bold" }}>{datos.porcentaje_general}%</p>
            </div>
            <div style={{ border: "1px solid #444", borderRadius: 8, padding: 16, minWidth: 200 }}>
              <p style={{ margin: 0, opacity: 0.7 }}>Cursos con sílabo</p>
              <p style={{ margin: 0, fontSize: 28, fontWeight: "bold" }}>
                {datos.total_cargados} / {datos.total_cursos}
              </p>
            </div>
          </div>

          <h3>Porcentaje cargado por especialidad</h3>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={datos.resumen_por_especialidad}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="especialidad" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Bar dataKey="porcentaje" name="Porcentaje cargado" fill="#6b6bff" />
            </BarChart>
          </ResponsiveContainer>

          <h3>Sílabos pendientes</h3>
          <table>
            <thead>
              <tr>
                <th>Curso</th>
                <th>Especialidad</th>
                <th>Docente responsable</th>
                <th>Correo</th>
              </tr>
            </thead>
            <tbody>
              {datos.pendientes.map((p) => (
                <tr key={p.oferta_academica_id} style={{ backgroundColor: "rgba(255, 165, 0, 0.15)" }}>
                  <td>{p.curso_nombre}</td>
                  <td>{p.especialidad}</td>
                  <td>{p.docente_nombre}</td>
                  <td>{p.docente_correo || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
