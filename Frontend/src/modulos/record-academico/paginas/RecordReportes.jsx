import { useEffect, useState } from "react";
import {
  reportesConsolidados,
  urlExportarReportesXlsx,
  listarAniosIngreso,
} from "../servicios/recordAcademicoServicio";
import { listarEspecialidades } from "../../administracion/servicios/administracionServicio";

export default function RecordReportes() {
  const [anios, setAnios] = useState([]);
  const [especialidades, setEspecialidades] = useState([]);
  const [filtros, setFiltros] = useState({ anioIngreso: "", especialidadId: "", estado: "" });
  const [filas, setFilas] = useState([]);
  const [error, setError] = useState(null);
  const [exportando, setExportando] = useState(false);

  useEffect(() => {
    cargarCatalogos();
  }, []);

  async function cargarCatalogos() {
    const [resAnios, resEspecialidades] = await Promise.all([
      listarAniosIngreso(),
      listarEspecialidades(),
    ]);
    if (!resAnios.error) setAnios(resAnios.data);
    if (!resEspecialidades.error) setEspecialidades(resEspecialidades.data);
  }

  function actualizarFiltro(campo, valor) {
    setFiltros((f) => ({ ...f, [campo]: valor }));
  }

  async function manejarGenerarReporte() {
    if (!filtros.anioIngreso || !filtros.especialidadId) {
      setError("Debes seleccionar Año de Ingreso y Especialidad");
      return;
    }

    const { data, error } = await reportesConsolidados(filtros);
    if (error) {
      setError(error);
      setFilas([]);
      return;
    }

    setError(null);
    setFilas(data);
  }

  async function manejarExportar() {
    setExportando(true);

    try {
      const token = localStorage.getItem("token");
      const respuesta = await fetch(urlExportarReportesXlsx(filtros), {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!respuesta.ok) {
        throw new Error("fallo");
      }

      const blob = await respuesta.blob();
      const objectUrl = window.URL.createObjectURL(blob);
      const enlace = document.createElement("a");
      enlace.href = objectUrl;
      enlace.download = "sabana_de_notas.xlsx";
      enlace.click();
      window.URL.revokeObjectURL(objectUrl);
    } catch (err) {
      setError("No se pudo exportar el reporte en este momento");
    } finally {
      setExportando(false);
    }
  }

  return (
    <div className="contenedor">
      <h2>Reportes consolidados</h2>
      <p>Filtra por Año de Ingreso y Especialidad para generar la sábana de notas.</p>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <select value={filtros.anioIngreso} onChange={(e) => actualizarFiltro("anioIngreso", e.target.value)}>
          <option value="">Año de ingreso</option>
          {anios.map((a) => (
            <option key={a} value={a}>{a}</option>
          ))}
        </select>

        <select value={filtros.especialidadId} onChange={(e) => actualizarFiltro("especialidadId", e.target.value)}>
          <option value="">Especialidad</option>
          {especialidades.map((e) => (
            <option key={e.id} value={e.id}>{e.nombre}</option>
          ))}
        </select>

        <select value={filtros.estado} onChange={(e) => actualizarFiltro("estado", e.target.value)}>
          <option value="">Todos los estados</option>
          <option value="Regular">Regular</option>
          <option value="Condicional">Condicional</option>
          <option value="Egresado">Egresado</option>
        </select>

        <button type="button" onClick={manejarGenerarReporte}>Generar Reporte</button>
      </div>

      {filas.length > 0 && (
        <>
          <table>
            <thead>
              <tr>
                <th>Código</th>
                <th>Nombres</th>
                <th>Créditos matriculados</th>
                <th>Créditos aprobados</th>
                <th>PPS último ciclo</th>
                <th>PPA</th>
              </tr>
            </thead>
            <tbody>
              {filas.map((f) => (
                <tr key={f.estudiante_id}>
                  <td>{f.codigo}</td>
                  <td>{f.nombres_completos}</td>
                  <td>{f.creditos_matriculados}</td>
                  <td>{f.creditos_aprobados}</td>
                  <td>{f.pps_ultimo_ciclo ?? "-"}</td>
                  <td>{f.ppa ?? "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <button type="button" onClick={manejarExportar} disabled={exportando} style={{ marginTop: 12 }}>
            {exportando ? "Generando..." : "Exportar a Excel"}
          </button>
        </>
      )}
    </div>
  );
}
