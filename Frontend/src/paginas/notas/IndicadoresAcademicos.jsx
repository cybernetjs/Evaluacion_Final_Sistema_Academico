import { useEffect, useState } from "react";
import { indicadoresDireccion } from "../../servicios/notas.servicio";
import { listarPeriodos } from "../../servicios/matricula.servicio";
import { listarEspecialidades, listarPlanesEstudio } from "../../servicios/administracion.servicio";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";

export default function IndicadoresAcademicos() {
  const [indicadores, setIndicadores] = useState(null);
  const [periodos, setPeriodos] = useState([]);
  const [especialidades, setEspecialidades] = useState([]);
  const [planes, setPlanes] = useState([]);
  const [filtros, setFiltros] = useState({ periodoAcademicoId: "", especialidadId: "", planEstudiosId: "" });
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    cargarCatalogos();
  }, []);

  useEffect(() => {
    cargarIndicadores();
  }, [filtros]);

  async function cargarCatalogos() {
    const [resPeriodos, resEspecialidades, resPlanes] = await Promise.all([
      listarPeriodos(),
      listarEspecialidades(),
      listarPlanesEstudio(),
    ]);
    if (!resPeriodos.error) setPeriodos(resPeriodos.data);
    if (!resEspecialidades.error) setEspecialidades(resEspecialidades.data);
    if (!resPlanes.error) setPlanes(resPlanes.data);
  }

  async function cargarIndicadores() {
    setCargando(true);
    const { data, error } = await indicadoresDireccion(filtros);
    setCargando(false);

    if (error) {
      setError(error);
      return;
    }
    setError(null);
    setIndicadores(data);
  }

  function actualizarFiltro(campo, valor) {
    setFiltros((f) => ({ ...f, [campo]: valor }));
  }

  return (
    <div className="contenedor">
      <h2>Indicadores Académicos</h2>

      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <select value={filtros.periodoAcademicoId} onChange={(e) => actualizarFiltro("periodoAcademicoId", e.target.value)}>
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

        <select value={filtros.planEstudiosId} onChange={(e) => actualizarFiltro("planEstudiosId", e.target.value)}>
          <option value="">Todas las mallas curriculares</option>
          {planes.map((p) => (
            <option key={p.id} value={p.id}>
              {p.nombre ?? `Plan #${p.id}`}
            </option>
          ))}
        </select>
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}
      {cargando && <p>Cargando...</p>}

      {!cargando && indicadores && (
        <>
          <div style={{ border: "1px solid #444", borderRadius: 8, padding: 16, maxWidth: 260, marginBottom: 24 }}>
            <p style={{ margin: 0, opacity: 0.7 }}>Deserción del periodo</p>
            <p style={{ margin: 0, fontSize: 28, fontWeight: "bold" }}>{indicadores.porcentaje_desercion}%</p>
          </div>

          <h3>Tasa de aprobación por asignatura y sección</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={indicadores.tasa_aprobacion_por_curso}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="curso_codigo" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Bar dataKey="tasa_aprobacion_porcentaje" name="% Aprobación">
                {indicadores.tasa_aprobacion_por_curso.map((entrada, index) => (
                  <Cell key={index} fill={entrada.seccion_critica ? "#ff6b6b" : "#6b6bff"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>

          <h3>Índice de desaprobación por especialidad</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={indicadores.desaprobacion_por_especialidad}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="especialidad" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Bar dataKey="tasa_desaprobacion_porcentaje" name="% Desaprobación" fill="#ff9f43" />
            </BarChart>
          </ResponsiveContainer>

          <h3>Secciones activas</h3>
          <table>
            <thead>
              <tr>
                <th>Curso</th>
                <th>Docente</th>
                <th>% Aprobación</th>
                <th>% Desaprobación</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {indicadores.tasa_aprobacion_por_curso.map((c) => (
                <tr
                  key={c.oferta_academica_id}
                  style={c.seccion_critica ? { color: "#ff6b6b", fontWeight: "bold" } : undefined}
                >
                  <td>{c.curso_codigo} — {c.curso_nombre}</td>
                  <td>{c.docente ?? "Sin asignar"}</td>
                  <td>{c.tasa_aprobacion_porcentaje}%</td>
                  <td>{c.tasa_desaprobacion_porcentaje}%</td>
                  <td>{c.seccion_critica ? "Sección Crítica" : "Normal"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
