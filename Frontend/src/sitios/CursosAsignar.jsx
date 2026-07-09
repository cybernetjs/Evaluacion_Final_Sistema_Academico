import { useEffect, useState } from "react";
import { listarOfertas } from "../servicios/matricula.servicio";
import {
  asignarDocente,
  gestionarHorario,
  listarCursos,
  listarDocentes,
  listarTiposDocentes,
} from "../servicios/cursosDocentes.servicio";

export default function CursosAsignar() {
  const [ofertas, setOfertas] = useState([]);
  const [cursos, setCursos] = useState([]);
  const [docentes, setDocentes] = useState([]);
  const [tiposDocentes, setTiposDocentes] = useState([]);
  const [ofertaId, setOfertaId] = useState("");
  const [docenteId, setDocenteId] = useState("");
  const [tipoDocenteId, setTipoDocenteId] = useState("");
  const [dia, setDia] = useState("Lunes");
  const [horaInicio, setHoraInicio] = useState("");
  const [horaFin, setHoraFin] = useState("");
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarDatos();
  }, []);

  async function cargarDatos() {
    const [resOfertas, resCursos, resDocentes, resTipos] = await Promise.all([
      listarOfertas(),
      listarCursos(),
      listarDocentes(),
      listarTiposDocentes(),
    ]);

    if (!resOfertas.error) {
      setOfertas(resOfertas.data);
      if (resOfertas.data?.length && !ofertaId) {
        setOfertaId(String(resOfertas.data[0].id));
      }
    }

    if (!resCursos.error) {
      setCursos(resCursos.data);
    }

    if (!resDocentes.error) {
      setDocentes(resDocentes.data);
      if (resDocentes.data?.length && !docenteId) {
        setDocenteId(String(resDocentes.data[0].id));
      }
    }

    if (!resTipos.error) {
      setTiposDocentes(resTipos.data);
      if (resTipos.data?.length && !tipoDocenteId) {
        setTipoDocenteId(String(resTipos.data[0].id));
      }
    }
  }

  function nombreCurso(cursoId) {
    const curso = cursos.find((item) => item.id === cursoId);
    if (!curso) return `Curso ${cursoId}`;
    return `${curso.codigo} - ${curso.nombre}`;
  }

  function textoOferta(oferta) {
    return `Oferta ${oferta.id} | ${nombreCurso(oferta.curso_id)} | Semestre ${oferta.semestre_id}`;
  }

  async function manejarAsignacion(evento) {
    evento.preventDefault();
    setMensaje(null);
    setError(null);

    const { data, error } = await asignarDocente(ofertaId, {
      docente_id: Number(docenteId),
      tipo_docente_id: Number(tipoDocenteId),
    });

    if (error) {
      setError(error);
      return;
    }

    setMensaje(data.mensaje);
  }

  async function manejarHorario(evento) {
    evento.preventDefault();
    setMensaje(null);
    setError(null);

    const { data, error } = await gestionarHorario(ofertaId, {
      dia,
      hora_inicio: horaInicio,
      hora_fin: horaFin,
    });

    if (error) {
      setError(error);
      return;
    }

    setMensaje(data.mensaje);
  }

  return (
    <div className="contenedor">
      <h2>Cursos y docentes</h2>
      <p>Gestiona la asignación de docentes y horarios de las ofertas académicas.</p>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      <div style={{ display: "grid", gap: "24px" }}>
        <form onSubmit={manejarAsignacion}>
          <h3>Asignar docente</h3>
          <div>
            <label>Oferta académica</label>
            <select value={ofertaId} onChange={(e) => setOfertaId(e.target.value)}>
              {ofertas.map((oferta) => (
                <option key={oferta.id} value={oferta.id}>
                  {textoOferta(oferta)}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label>Docente</label>
            <select value={docenteId} onChange={(e) => setDocenteId(e.target.value)}>
              {docentes.map((docente) => (
                <option key={docente.id} value={docente.id}>
                  {docente.nombres} {docente.apellido_paterno}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label>Tipo de docente</label>
            <select value={tipoDocenteId} onChange={(e) => setTipoDocenteId(e.target.value)}>
              {tiposDocentes.map((tipo) => (
                <option key={tipo.id} value={tipo.id}>
                  {tipo.nombre}
                </option>
              ))}
            </select>
          </div>
          <button type="submit">Asignar docente</button>
        </form>

        <form onSubmit={manejarHorario}>
          <h3>Registrar horario</h3>
          <div>
            <label>Oferta académica</label>
            <select value={ofertaId} onChange={(e) => setOfertaId(e.target.value)}>
              {ofertas.map((oferta) => (
                <option key={oferta.id} value={oferta.id}>
                  {textoOferta(oferta)}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label>Día</label>
            <input value={dia} onChange={(e) => setDia(e.target.value)} />
          </div>
          <div>
            <label>Hora inicio</label>
            <input type="time" value={horaInicio} onChange={(e) => setHoraInicio(e.target.value)} />
          </div>
          <div>
            <label>Hora fin</label>
            <input type="time" value={horaFin} onChange={(e) => setHoraFin(e.target.value)} />
          </div>
          <button type="submit">Guardar horario</button>
        </form>
      </div>

      <table>
        <thead>
          <tr>
            <th>Oferta</th>
            <th>Curso</th>
            <th>Semestre</th>
            <th>Periodo</th>
            <th>Cupos</th>
          </tr>
        </thead>
        <tbody>
          {ofertas.map((oferta) => (
            <tr key={oferta.id}>
              <td>{oferta.id}</td>
              <td>{nombreCurso(oferta.curso_id)}</td>
              <td>{oferta.semestre_id}</td>
              <td>{oferta.periodo_academico_id}</td>
              <td>{oferta.cupos}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
