import { useEffect, useState } from "react";
import { cargaDocente, evaluarCumplimientoPlan, listarCursos } from "../servicios/cursosDocentes.servicio";
import { listarPeriodos } from "../servicios/matricula.servicio";

export default function CursosCargaDocente() {
  const [carga, setCarga] = useState([]);
  const [cursos, setCursos] = useState([]);
  const [periodos, setPeriodos] = useState([]);
  const [periodoAcademicoId, setPeriodoAcademicoId] = useState("");
  const [cumplimiento, setCumplimiento] = useState([]);
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarDatos();
  }, []);

  async function cargarDatos() {
    const [resCarga, resCursos, resPeriodos] = await Promise.all([
      cargaDocente(),
      listarCursos(),
      listarPeriodos(),
    ]);

    if (resCarga.error) {
      setError(resCarga.error);
    } else {
      setCarga(resCarga.data);
    }

    if (!resCursos.error) {
      setCursos(resCursos.data);
    }

    if (!resPeriodos.error) {
      setPeriodos(resPeriodos.data);
      if (resPeriodos.data?.length && !periodoAcademicoId) {
        setPeriodoAcademicoId(String(resPeriodos.data[0].id));
      }
    }
  }

  function nombreCurso(cursoId) {
    const curso = cursos.find((item) => item.id === cursoId);
    if (!curso) return `Curso ${cursoId}`;
    return `${curso.codigo} - ${curso.nombre}`;
  }

  async function manejarCumplimiento(evento) {
    evento.preventDefault();
    setMensaje(null);
    setError(null);

    const { data, error } = await evaluarCumplimientoPlan(periodoAcademicoId);

    if (error) {
      setError(error);
      return;
    }

    setCumplimiento(data);
    setMensaje("Cumplimiento del plan cargado correctamente");
  }

  return (
    <div className="contenedor">
      <h2>Carga docente</h2>
      <p>Supervisa la distribución de cursos y el cumplimiento del plan de estudios.</p>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      <form onSubmit={manejarCumplimiento}>
        <div>
          <label>Periodo académico</label>
          <select value={periodoAcademicoId} onChange={(e) => setPeriodoAcademicoId(e.target.value)} required>
            <option value="">Selecciona un periodo</option>
            {periodos.map((periodo) => (
              <option key={periodo.id} value={periodo.id}>
                {periodo.nombre || `Periodo ${periodo.id}`}
              </option>
            ))}
          </select>
        </div>
        <button type="submit">Evaluar cumplimiento</button>
      </form>

      <h3>Carga por docente</h3>
      <table>
        <thead>
          <tr>
            <th>Docente</th>
            <th>Cursos asignados</th>
          </tr>
        </thead>
        <tbody>
          {carga.map((item) => (
            <tr key={item.docente_id}>
              <td>{item.nombres} {item.apellido_paterno}</td>
              <td>{item.cursos_asignados}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Cumplimiento del plan</h3>
      <table>
        <thead>
          <tr>
            <th>Curso</th>
            <th>Docentes asignados</th>
            <th>Cupos</th>
          </tr>
        </thead>
        <tbody>
          {cumplimiento.map((item, index) => (
            <tr key={`${item.curso_id}-${index}`}>
              <td>{nombreCurso(item.curso_id)}</td>
              <td>{item.docentes_asignados}</td>
              <td>{item.cupos}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
