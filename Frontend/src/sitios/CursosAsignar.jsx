import { useEffect, useState } from "react";
import { listarOfertas } from "../servicios/matricula.servicio";
import {
  asignarDocente,
  gestionarHorario,
  listarDocentes,
  obtenerCurso,
} from "../servicios/cursosDocentes.servicio";

const DIAS = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"];

export default function CursosAsignar() {
  const [ofertas, setOfertas] = useState([]);
  const [docentes, setDocentes] = useState([]);
  const [ofertaId, setOfertaId] = useState("");
  const [cursoSeleccionado, setCursoSeleccionado] = useState(null);
  const [docenteId, setDocenteId] = useState("");
  const [funcionCurso, setFuncionCurso] = useState("Teorico");
  const [horasAsignadas, setHorasAsignadas] = useState("");
  const [dia, setDia] = useState("Lunes");
  const [horaInicio, setHoraInicio] = useState("");
  const [horaFin, setHoraFin] = useState("");
  const [aula, setAula] = useState("");
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarDatos();
  }, []);

  useEffect(() => {
    if (!ofertaId) {
      setCursoSeleccionado(null);
      return;
    }
    const oferta = ofertas.find((o) => String(o.id) === ofertaId);
    if (oferta) {
      obtenerCurso(oferta.curso_id).then((res) => {
        if (!res.error) setCursoSeleccionado(res.data);
      });
    }
  }, [ofertaId, ofertas]);

  async function cargarDatos() {
    const [resOfertas, resDocentes] = await Promise.all([
      listarOfertas(),
      listarDocentes(),
    ]);

    if (!resOfertas.error) {
      setOfertas(resOfertas.data);
      if (resOfertas.data?.length && !ofertaId) {
        setOfertaId(String(resOfertas.data[0].id));
      }
    }

    if (!resDocentes.error) {
      setDocentes(resDocentes.data);
      if (resDocentes.data?.length && !docenteId) {
        setDocenteId(String(resDocentes.data[0].id));
      }
    }
  }

  const horasRequeridasCurso = cursoSeleccionado
    ? cursoSeleccionado.horas_lectivas + cursoSeleccionado.horas_practicas
    : null;

  async function manejarAsignacion(evento) {
    evento.preventDefault();
    setMensaje(null);
    setError(null);

    if (!horasAsignadas || Number(horasAsignadas) <= 0) {
      setError("Debes ingresar un número entero positivo de horas asignadas");
      return;
    }

    const { data, error } = await asignarDocente(ofertaId, {
      docente_id: Number(docenteId),
      funcion_curso: funcionCurso,
      horas_asignadas: Number(horasAsignadas),
    });

    if (error) {
      setError(error);
      return;
    }

    setMensaje(`Asignación registrada. Estado de la sección: ${data.estado_seccion}`);
    setHorasAsignadas("");
  }

  async function manejarHorario(evento) {
    evento.preventDefault();
    setMensaje(null);
    setError(null);

    if (!aula) {
      setError("Debes indicar el aula o el enlace virtual");
      return;
    }

    const { data, error } = await gestionarHorario(ofertaId, {
      dia,
      hora_inicio: horaInicio,
      hora_fin: horaFin,
      aula,
    });

    if (error) {
      setError(error);
      return;
    }

    setMensaje(`Horario registrado con estado: ${data.estado}`);
  }

  return (
    <div className="contenedor">
      <h2>Cursos y docentes</h2>
      <p>Gestiona la asignación de docentes y horarios de las ofertas académicas.</p>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      <div>
        <label>Oferta académica</label>
        <select value={ofertaId} onChange={(e) => setOfertaId(e.target.value)}>
          {ofertas.map((o) => (
            <option key={o.id} value={o.id}>
              {o.curso_nombre} - Semestre {o.semestre_codigo}
            </option>
          ))}
        </select>
      </div>

      {cursoSeleccionado && (
        <p>
          Horas requeridas del curso: {horasRequeridasCurso} ({cursoSeleccionado.horas_lectivas} teóricas
          + {cursoSeleccionado.horas_practicas} prácticas)
        </p>
      )}

      <h3>Asignar docente</h3>
      <form onSubmit={manejarAsignacion}>
        <div>
          <label>Docente</label>
          <select value={docenteId} onChange={(e) => setDocenteId(e.target.value)}>
            {docentes.map((d) => (
              <option key={d.id} value={d.id}>
                {d.nombres} {d.apellido_paterno}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label>Tipo de docente</label>
          <select value={funcionCurso} onChange={(e) => setFuncionCurso(e.target.value)}>
            <option value="Teorico">Teórico</option>
            <option value="Practico">Práctico</option>
          </select>
        </div>

        <div>
          <label>Horas asignadas</label>
          <input
            type="number"
            min="1"
            step="1"
            value={horasAsignadas}
            onChange={(e) => setHorasAsignadas(e.target.value)}
          />
        </div>

        <button type="submit">Guardar Asignación</button>
      </form>

      <h3>Registrar horario y aula</h3>
      <form onSubmit={manejarHorario}>
        <div>
          <label>Día</label>
          <select value={dia} onChange={(e) => setDia(e.target.value)}>
            {DIAS.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>

        <div>
          <label>Hora de inicio</label>
          <input type="time" value={horaInicio} onChange={(e) => setHoraInicio(e.target.value)} />
        </div>

        <div>
          <label>Hora de fin</label>
          <input
            type="time"
            value={horaFin}
            min={horaInicio || undefined}
            onChange={(e) => setHoraFin(e.target.value)}
          />
        </div>

        <div>
          <label>Aula o enlace virtual</label>
          <input type="text" value={aula} onChange={(e) => setAula(e.target.value)} />
        </div>

        <button type="submit">Guardar horario</button>
      </form>
    </div>
  );
}
