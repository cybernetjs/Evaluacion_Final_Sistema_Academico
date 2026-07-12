import { useState, useEffect } from "react";
import {
  obtenerEstadisticas,
  urlExportarReporte,
  listarPeriodos,
} from "../../servicios/matricula.servicio";
import { listarEspecialidades } from "../../servicios/administracion.servicio";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export default function EstadisticasMatricula() {
  const [estadisticas, setEstadisticas] = useState(null);
  const [periodos, setPeriodos] = useState([]);
  const [especialidades, setEspecialidades] = useState([]);
  const [filtros, setFiltros] = useState({ periodoId: "", especialidadId: "" });
  const [formatoExportar, setFormatoExportar] = useState("csv");
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarCatalogos();
  }, []);

  useEffect(() => {
    cargarEstadisticas();
  }, [filtros]);

  async function cargarCatalogos() {
    const [resPeriodos, resEspecialidades] = await Promise.all([
      listarPeriodos(),
      listarEspecialidades(),
    ]);
    if (!resPeriodos.error) setPeriodos(resPeriodos.data);
    if (!resEspecialidades.error) setEspecialidades(resEspecialidades.data);
  }

  async function cargarEstadisticas() {
    const { data, error } = await obtenerEstadisticas(filtros);
    if (error) {
      setError(error);
      return;
    }
    setError(null);
    setEstadisticas(data);
  }

  function actualizarFiltro(campo, valor) {
    setFiltros((f) => ({ ...f, [campo]: valor }));
  }

  function manejarExportar() {
    const url = urlExportarReporte({ ...filtros, formato: formatoExportar });
    const token = localStorage.getItem("token");

    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((respuesta) => respuesta.blob())
      .then((blob) => {
        const objectUrl = window.URL.createObjectURL(blob);
        const enlace = document.createElement("a");
        enlace.href = objectUrl;
        enlace.download = `reporte_matriculas.${formatoExportar}`;
        enlace.click();
        window.URL.revokeObjectURL(objectUrl);
      });
  }

  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (!estadisticas) return <p>Cargando...</p>;

  return (
    <div className="contenedor">
      <h2>Estadísticas de Matrícula</h2>

      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <select value={filtros.periodoId} onChange={(e) => actualizarFiltro("periodoId", e.target.value)}>
          <option value="">Todos los ciclos</option>
          {periodos.map((p) => (
            <option key={p.id} value={p.id}>
              {p.nombre}
            </option>
          ))}
        </select>

        <select value={filtros.especialidadId} onChange={(e) => actualizarFiltro("especialidadId", e.target.value)}>
          <option value="">Todas las especialidades</option>
          {especialidades.map((e) => (
            <option key={e.id} value={e.id}>
              {e.nombre}
            </option>
          ))}
        </select>
      </div>

      <div style={{ display: "flex", gap: 16, marginBottom: 24 }}>
        <div style={{ border: "1px solid #444", borderRadius: 8, padding: 16, minWidth: 180 }}>
          <p style={{ margin: 0, opacity: 0.7 }}>Total Matriculados</p>
          <p style={{ margin: 0, fontSize: 28, fontWeight: "bold" }}>{estadisticas.total_matriculados}</p>
        </div>
        <div style={{ border: "1px solid #444", borderRadius: 8, padding: 16, minWidth: 180 }}>
          <p style={{ margin: 0, opacity: 0.7 }}>Pendientes de Validación</p>
          <p style={{ margin: 0, fontSize: 28, fontWeight: "bold" }}>{estadisticas.total_pendientes}</p>
        </div>
        <div style={{ border: "1px solid #444", borderRadius: 8, padding: 16, minWidth: 180 }}>
          <p style={{ margin: 0, opacity: 0.7 }}>Avance vs. semestre anterior</p>
          <p style={{ margin: 0, fontSize: 28, fontWeight: "bold" }}>
            {estadisticas.ratio_avance_porcentaje === null ? "Sin datos" : `${estadisticas.ratio_avance_porcentaje}%`}
          </p>
        </div>
      </div>

      <h3>Demanda académica por ciclo y especialidad</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={estadisticas.matriculados_por_ciclo}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="ciclo" />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Legend />
          <Bar dataKey="total" name="Estudiantes matriculados" fill="#6b6bff" />
        </BarChart>
      </ResponsiveContainer>

      <h3>Top 5 cursos con mayor demanda</h3>
      <table>
        <thead>
          <tr>
            <th>Curso</th>
            <th>Matriculados</th>
            <th>Ocupación</th>
            <th>Sección crítica</th>
          </tr>
        </thead>
        <tbody>
          {estadisticas.top_cursos.map((c) => (
            <tr key={c.curso}>
              <td>{c.curso}</td>
              <td>{c.matriculados}</td>
              <td>{c.ocupacion_porcentaje}%</td>
              <td style={{ color: c.seccion_critica ? "#ff6b6b" : undefined }}>
                {c.seccion_critica ? "Sí" : "No"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{ display: "flex", gap: 8, marginTop: 24, alignItems: "center" }}>
        <select value={formatoExportar} onChange={(e) => setFormatoExportar(e.target.value)}>
          <option value="csv">CSV</option>
          <option value="xlsx">Excel (XLSX)</option>
        </select>
        <button type="button" onClick={manejarExportar}>
          Exportar Reporte
        </button>
      </div>
    </div>
  );
}
