import { useEffect, useState } from "react";
import { miHistorial, urlDescargarHistorialPdf } from "../servicios/recordAcademicoServicio";

export default function RecordMiHistorial() {
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState(null);
  const [descargando, setDescargando] = useState(false);
  const [errorDescarga, setErrorDescarga] = useState(null);

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

  async function manejarDescargarPdf() {
    setDescargando(true);
    setErrorDescarga(null);

    try {
      const token = localStorage.getItem("token");
      const respuesta = await fetch(urlDescargarHistorialPdf(), {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!respuesta.ok) {
        throw new Error("fallo");
      }

      const blob = await respuesta.blob();
      const objectUrl = window.URL.createObjectURL(blob);
      const enlace = document.createElement("a");
      enlace.href = objectUrl;
      enlace.download = "reporte_informativo_historial.pdf";
      enlace.click();
      window.URL.revokeObjectURL(objectUrl);
    } catch (err) {
      setErrorDescarga("No se pudo generar el documento en este momento. Por favor, intente nuevamente.");
    } finally {
      setDescargando(false);
    }
  }

  return (
    <div className="contenedor">
      <h2>Mi historial academico</h2>
      <p className="texto-descripcion">
        Revisa tu historial completo, del semestre mas reciente al mas antiguo.
      </p>

      {error && <p style={{ color: "red" }}>{error}</p>}
      {errorDescarga && <p style={{ color: "red" }}>{errorDescarga}</p>}

      {datos && (
        <>
          <div className="resumen-historial">
            <div className="resumen-card">
              <p>Creditos matriculados</p>
              <strong>{datos.cabecera.total_creditos_matriculados}</strong>
            </div>
            <div className="resumen-card">
              <p>Creditos aprobados</p>
              <strong>{datos.cabecera.total_creditos_aprobados}</strong>
            </div>
            <div className="resumen-card">
              <p>Promedio ponderado acumulado</p>
              <strong>{datos.cabecera.promedio_ponderado_acumulado ?? "Sin datos"}</strong>
            </div>
          </div>

          <button type="button" onClick={manejarDescargarPdf} disabled={descargando}>
            {descargando ? "Generando..." : "Descargar Record Informativo"}
          </button>

          <table style={{ marginTop: 16 }}>
            <thead>
              <tr>
                <th>Periodo</th>
                <th>Semestre</th>
                <th>Codigo</th>
                <th>Curso</th>
                <th>Creditos</th>
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
