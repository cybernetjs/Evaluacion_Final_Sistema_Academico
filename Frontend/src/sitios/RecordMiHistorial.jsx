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
      <p>Revisa tu historial completo, del semestre más reciente al más antiguo.</p>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {datos && (
        <>

          <div style={{ display: "flex", gap: 16, marginBottom: 24 }}>
            <div style={{ border: "1px solid #444", borderRadius: 8, padding: 16, minWidth: 180 }}>
              <p style={{ margin: 0, opacity: 0.7 }}>Créditos matriculados</p>
              <p style={{ margin: 0, fontSize: 28, fontWeight: "bold" }}>
                {datos.cabecera.total_creditos_matriculados}
              </p>
            </div>
            <div style={{ border: "1px solid #444", borderRadius: 8, padding: 16, minWidth: 180 }}>
              <p style={{ margin: 0, opacity: 0.7 }}>Créditos aprobados</p>
              <p style={{ margin: 0, fontSize: 28, fontWeight: "bold" }}>
                {datos.cabecera.total_creditos_aprobados}
              </p>
            </div>
            <div style={{ border: "1px solid #444", borderRadius: 8, padding: 16, minWidth: 180 }}>
              <p style={{ margin: 0, opacity: 0.7 }}>Promedio ponderado acumulado</p>
              <p style={{ margin: 0, fontSize: 28, fontWeight: "bold" }}>
                {datos.cabecera.promedio_ponderado_acumulado ?? "Sin datos"}
              </p>
            </div>
          </div>

          <table>
            <thead>
              <tr>
                <th>Periodo</th>
                <th>Semestre</th>
                <th>Código</th>
                <th>Curso</th>
                <th>Créditos</th>
                <th>Nota final</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {datos.historial.map((fila, index) => {

                const desaprobado = fila.estado && fila.estado.toLowerCase() === "desaprobado";

                return (
                  <tr
                    key={`${fila.codigo_curso}-${index}`}
                    style={desaprobado ? { backgroundColor: "rgba(255, 0, 0, 0.12)" } : undefined}
                  >
                    <td>{fila.periodo_academico}</td>
                    <td>{fila.semestre}</td>
                    <td>{fila.codigo_curso}</td>
                    <td>{fila.nombre_curso}</td>
                    <td>{fila.creditos}</td>
                    <td>{fila.nota_final ?? "-"}</td>
                    <td style={desaprobado ? { color: "#c0392b", fontWeight: "bold" } : undefined}>
                      {fila.estado}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
