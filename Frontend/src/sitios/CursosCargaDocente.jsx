import { useEffect, useState } from "react";
import { cargaDocente } from "../servicios/cursosDocentes.servicio";
import { listarEspecialidades } from "../servicios/administracion.servicio";

const COLOR_POR_CATEGORIA = {
  "Carga Incompleta": "#f2c14e",
  "Carga Regular": "#4caf50",
  "Sobrecarga Laboral": "#e74c3c",
};

export default function CursosCargaDocente() {
  const [carga, setCarga] = useState([]);
  const [especialidades, setEspecialidades] = useState([]);
  const [especialidadId, setEspecialidadId] = useState("");
  const [docenteExpandido, setDocenteExpandido] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    listarEspecialidades().then((res) => {
      if (!res.error) setEspecialidades(res.data);
    });
    cargarDatos();
  }, []);

  async function cargarDatos(filtros = {}) {
    const { data, error } = await cargaDocente(filtros);
    if (error) {
      setError(error);
      return;
    }
    setError(null);
    setCarga(data);
  }

  function manejarFiltroEspecialidad(valor) {
    setEspecialidadId(valor);
    cargarDatos({ especialidadId: valor || undefined });
  }

  function alternarExpandido(docenteId) {
    setDocenteExpandido((actual) => (actual === docenteId ? null : docenteId));
  }

  return (
    <div className="contenedor">
      <h2>Distribución de carga lectiva</h2>
      <p>Panel analítico de la plana docente de la facultad para el periodo en curso.</p>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <select value={especialidadId} onChange={(e) => manejarFiltroEspecialidad(e.target.value)}>
        <option value="">Todas las especialidades</option>
        {especialidades.map((e) => (
          <option key={e.id} value={e.id}>{e.nombre}</option>
        ))}
      </select>

      <table style={{ marginTop: 16 }}>
        <thead>
          <tr>
            <th>Docente</th>
            <th>Especialidad</th>
            <th>Horas semanales</th>
            <th>Categoría</th>
          </tr>
        </thead>
        <tbody>
          {carga.map((item) => (
            <>
              <tr
                key={item.docente_id}
                onClick={() => alternarExpandido(item.docente_id)}
                style={{ cursor: "pointer" }}
              >
                <td>{item.nombres} {item.apellido_paterno}</td>
                <td>{item.especialidad || "-"}</td>
                <td>{item.total_horas_semanales}</td>
                <td>
                  <span
                    style={{
                      padding: "2px 8px",
                      borderRadius: 12,
                      color: "#fff",
                      backgroundColor: COLOR_POR_CATEGORIA[item.categoria],
                    }}
                  >
                    {item.categoria}
                  </span>
                </td>
              </tr>
              {docenteExpandido === item.docente_id && (
                <tr key={`${item.docente_id}-detalle`}>
                  <td colSpan={4}>
                    <table>
                      <thead>
                        <tr>
                          <th>Curso</th>
                          <th>Función</th>
                          <th>Horas</th>
                        </tr>
                      </thead>
                      <tbody>
                        {item.detalle_cursos.map((c, indice) => (
                          <tr key={indice}>
                            <td>{c.curso_nombre}</td>
                            <td>{c.funcion_curso}</td>
                            <td>{c.horas_asignadas}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </td>
                </tr>
              )}
            </>
          ))}
        </tbody>
      </table>
    </div>
  );
}
