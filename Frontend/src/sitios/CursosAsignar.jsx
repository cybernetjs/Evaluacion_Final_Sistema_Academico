import { useEffect, useState } from "react";
import { listarOfertas, obtenerPeriodoActual } from "../servicios/matricula.servicio";
import { listarSemestres } from "../servicios/administracion.servicio";
import {
  asignarDocente,
  crearCurso,
  crearOfertaAcademica,
  gestionarHorario,
  listarCursos,
  listarDocentes,
  obtenerAsignacionesOferta,
  obtenerCurso,
} from "../servicios/cursosDocentes.servicio";

const DIAS = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"];

const ETIQUETA_FUNCION = {
  Teorico: "Teórico",
  Practico: "Práctico",
};

export default function CursosAsignar() {
  const [ofertas, setOfertas] = useState([]);
  const [docentes, setDocentes] = useState([]);
  const [ofertaId, setOfertaId] = useState("");
  const [cursoSeleccionado, setCursoSeleccionado] = useState(null);
  const [asignaciones, setAsignaciones] = useState(null);
  const [docenteId, setDocenteId] = useState("");
  const [funcionCurso, setFuncionCurso] = useState("");
  const [horasAsignadas, setHorasAsignadas] = useState("");
  const [dia, setDia] = useState("Lunes");
  const [horaInicio, setHoraInicio] = useState("");
  const [horaFin, setHoraFin] = useState("");
  const [aula, setAula] = useState("");
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);

  const [mostrarFormCurso, setMostrarFormCurso] = useState(false);
  const [cursos, setCursos] = useState([]);
  const [nuevoCurso, setNuevoCurso] = useState({
    nombre: "",
    codigo: "",
    creditos: "",
    horas_lectivas: "",
    horas_practicas: "",
  });
  const [mensajeCurso, setMensajeCurso] = useState(null);
  const [errorCurso, setErrorCurso] = useState(null);

  const [mostrarFormSeccion, setMostrarFormSeccion] = useState(false);
  const [semestres, setSemestres] = useState([]);
  const [periodoActual, setPeriodoActual] = useState(null);
  const [nuevaSeccion, setNuevaSeccion] = useState({ curso_id: "", semestre_id: "", cupos: "" });
  const [mensajeSeccion, setMensajeSeccion] = useState(null);
  const [errorSeccion, setErrorSeccion] = useState(null);

  useEffect(() => {
    cargarDatos();
  }, []);

  useEffect(() => {
    if (!ofertaId) {
      setCursoSeleccionado(null);
      setAsignaciones(null);
      return;
    }
    const oferta = ofertas.find((o) => String(o.id) === ofertaId);
    if (oferta) {
      obtenerCurso(oferta.curso_id).then((res) => {
        if (!res.error) setCursoSeleccionado(res.data);
      });
    }
    cargarAsignaciones();
  }, [ofertaId, ofertas]);

  async function cargarDatos() {
    const [resOfertas, resDocentes, resCursos, resSemestres, resPeriodo] = await Promise.all([
      listarOfertas(),
      listarDocentes(),
      listarCursos(),
      listarSemestres(),
      obtenerPeriodoActual(),
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

    if (!resCursos.error) setCursos(resCursos.data);
    if (!resSemestres.error) setSemestres(resSemestres.data);
    if (!resPeriodo.error) setPeriodoActual(resPeriodo.data);
  }

  async function cargarAsignaciones() {
    const { data, error } = await obtenerAsignacionesOferta(ofertaId);
    if (!error) {
      setAsignaciones(data);
      // Preselecciona automáticamente la función que todavía falta por cubrir
      if (data.funciones_pendientes?.length === 1) {
        setFuncionCurso(data.funciones_pendientes[0]);
      } else if (data.funciones_pendientes?.length > 1) {
        setFuncionCurso("");
      }
    }
  }

  const horasRequeridasCurso = cursoSeleccionado
    ? cursoSeleccionado.horas_lectivas + cursoSeleccionado.horas_practicas
    : null;

  const funcionesPendientes = asignaciones?.funciones_pendientes ?? ["Teorico", "Practico"];
  const seccionCompleta = asignaciones?.plana_completa ?? false;

  async function manejarAsignacion(evento) {
    evento.preventDefault();
    setMensaje(null);
    setError(null);

    if (!funcionCurso) {
      setError("Selecciona el tipo de docente (Teórico o Práctico) que vas a registrar");
      return;
    }

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
    cargarAsignaciones();
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
    cargarAsignaciones();
  }

  async function manejarCrearCurso(evento) {
    evento.preventDefault();
    setMensajeCurso(null);
    setErrorCurso(null);

    const { data, error } = await crearCurso({
      nombre: nuevoCurso.nombre,
      codigo: nuevoCurso.codigo,
      creditos: Number(nuevoCurso.creditos),
      horas_lectivas: Number(nuevoCurso.horas_lectivas),
      horas_practicas: Number(nuevoCurso.horas_practicas),
    });

    if (error) {
      setErrorCurso(error);
      return;
    }

    setMensajeCurso(`Curso "${data.nombre}" (${data.codigo}) registrado correctamente`);
    setNuevoCurso({ nombre: "", codigo: "", creditos: "", horas_lectivas: "", horas_practicas: "" });
    const resCursos = await listarCursos();
    if (!resCursos.error) setCursos(resCursos.data);
  }

  async function manejarCrearSeccion(evento) {
    evento.preventDefault();
    setMensajeSeccion(null);
    setErrorSeccion(null);

    if (!periodoActual) {
      setErrorSeccion("No se pudo determinar el periodo académico vigente");
      return;
    }

    const { data, error } = await crearOfertaAcademica({
      curso_id: Number(nuevaSeccion.curso_id),
      periodo_academico_id: periodoActual.id,
      semestre_id: Number(nuevaSeccion.semestre_id),
      cupos: nuevaSeccion.cupos ? Number(nuevaSeccion.cupos) : undefined,
    });

    if (error) {
      setErrorSeccion(error);
      return;
    }

    setMensajeSeccion(`Sección de "${data.curso_nombre}" abierta correctamente para ${periodoActual.nombre}`);
    setNuevaSeccion({ curso_id: "", semestre_id: "", cupos: "" });
    const resOfertas = await listarOfertas();
    if (!resOfertas.error) {
      setOfertas(resOfertas.data);
      setOfertaId(String(data.id));
    }
  }

  return (
    <div className="contenedor">
      <h2>Cursos y docentes</h2>
      <p>Gestiona el catálogo de cursos, la apertura de secciones y la asignación de docentes y horarios.</p>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      <div style={{ border: "1px solid #444", borderRadius: 8, padding: 16, marginBottom: 20 }}>
        <button type="button" onClick={() => setMostrarFormCurso((v) => !v)}>
          {mostrarFormCurso ? "Ocultar" : "Registrar nuevo curso"}
        </button>
        <p style={{ marginTop: 8, color: "#aaa" }}>
          Un "curso" es la materia en sí (por ejemplo, Redes de Computadoras). Una vez registrado el curso,
          debes abrir una sección (oferta académica) para el periodo vigente antes de poder asignarle
          docente y horario.
        </p>

        {mostrarFormCurso && (
          <form onSubmit={manejarCrearCurso} style={{ marginTop: 12 }}>
            {mensajeCurso && <p style={{ color: "green" }}>{mensajeCurso}</p>}
            {errorCurso && <p style={{ color: "red" }}>{errorCurso}</p>}

            <div>
              <label>Nombre del curso</label>
              <input
                type="text"
                value={nuevoCurso.nombre}
                onChange={(e) => setNuevoCurso({ ...nuevoCurso, nombre: e.target.value })}
                required
              />
            </div>
            <div>
              <label>Código</label>
              <input
                type="text"
                placeholder="Ej. RED1"
                value={nuevoCurso.codigo}
                onChange={(e) => setNuevoCurso({ ...nuevoCurso, codigo: e.target.value })}
                required
              />
            </div>
            <div>
              <label>Créditos</label>
              <input
                type="number"
                min="1"
                value={nuevoCurso.creditos}
                onChange={(e) => setNuevoCurso({ ...nuevoCurso, creditos: e.target.value })}
                required
              />
            </div>
            <div>
              <label>Horas teóricas semanales</label>
              <input
                type="number"
                min="0"
                value={nuevoCurso.horas_lectivas}
                onChange={(e) => setNuevoCurso({ ...nuevoCurso, horas_lectivas: e.target.value })}
                required
              />
            </div>
            <div>
              <label>Horas prácticas semanales</label>
              <input
                type="number"
                min="0"
                value={nuevoCurso.horas_practicas}
                onChange={(e) => setNuevoCurso({ ...nuevoCurso, horas_practicas: e.target.value })}
                required
              />
            </div>
            <button type="submit">Guardar curso</button>
          </form>
        )}
      </div>

      <div style={{ border: "1px solid #444", borderRadius: 8, padding: 16, marginBottom: 20 }}>
        <button type="button" onClick={() => setMostrarFormSeccion((v) => !v)}>
          {mostrarFormSeccion ? "Ocultar" : "Abrir sección para el periodo vigente"}
        </button>
        <p style={{ marginTop: 8, color: "#aaa" }}>
          Elige un curso ya registrado y el semestre del plan de estudios al que pertenece. Esto crea la
          "oferta académica" (sección) que luego aparece en el desplegable de abajo para asignar docente y
          horario. {periodoActual ? `Periodo vigente: ${periodoActual.nombre}.` : ""}
        </p>

        {mostrarFormSeccion && (
          <form onSubmit={manejarCrearSeccion} style={{ marginTop: 12 }}>
            {mensajeSeccion && <p style={{ color: "green" }}>{mensajeSeccion}</p>}
            {errorSeccion && <p style={{ color: "red" }}>{errorSeccion}</p>}

            <div>
              <label>Curso</label>
              <select
                value={nuevaSeccion.curso_id}
                onChange={(e) => setNuevaSeccion({ ...nuevaSeccion, curso_id: e.target.value })}
                required
              >
                <option value="">Selecciona un curso</option>
                {cursos.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.nombre} ({c.codigo})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label>Semestre del plan de estudios</label>
              <select
                value={nuevaSeccion.semestre_id}
                onChange={(e) => setNuevaSeccion({ ...nuevaSeccion, semestre_id: e.target.value })}
                required
              >
                <option value="">Selecciona un semestre</option>
                {semestres.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.codigo}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label>Cupos (opcional, por defecto 40)</label>
              <input
                type="number"
                min="1"
                value={nuevaSeccion.cupos}
                onChange={(e) => setNuevaSeccion({ ...nuevaSeccion, cupos: e.target.value })}
              />
            </div>
            <button type="submit">Abrir sección</button>
          </form>
        )}
      </div>

      <div>
        <label>Oferta académica (sección)</label>
        <select value={ofertaId} onChange={(e) => setOfertaId(e.target.value)}>
          {ofertas.map((o) => (
            <option key={o.id} value={o.id}>
              {o.curso_nombre} - Semestre {o.semestre_codigo} (sección S-{o.id})
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

      {asignaciones && (
        <div style={{ marginBottom: 16 }}>
          <h4>Docentes ya asignados a esta sección</h4>
          {asignaciones.docentes_asignados.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>Docente</th>
                  <th>Tipo</th>
                  <th>Horas asignadas</th>
                </tr>
              </thead>
              <tbody>
                {asignaciones.docentes_asignados.map((a) => (
                  <tr key={a.asignacion_id}>
                    <td>{a.docente_nombre}</td>
                    <td>{ETIQUETA_FUNCION[a.funcion_curso] ?? a.funcion_curso}</td>
                    <td>{a.horas_asignadas}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>Todavía no hay docentes asignados a esta sección.</p>
          )}

          {seccionCompleta ? (
            <p style={{ color: "#8fd18f" }}>
              La plana docente de esta sección está completa (cubre las horas teóricas y prácticas
              requeridas).
            </p>
          ) : (
            <p style={{ color: "#f0ad4e" }}>
              Falta asignar: {funcionesPendientes.map((f) => ETIQUETA_FUNCION[f] ?? f).join(", ")}. Cada
              sección necesita, como máximo, un docente Teórico y un docente Práctico — un mismo docente
              puede cubrir ambos roles en distintas secciones, pero no dos veces el mismo rol en la misma
              sección.
            </p>
          )}
        </div>
      )}

      <h3>Asignar docente a la sección</h3>
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
          <p style={{ color: "#aaa", fontSize: "0.9em" }}>
            Solo aparecen aquí los docentes ya registrados por Administración (menú "Registrar docente").
            Si no encuentras al docente que buscas, primero debes registrarlo ahí; después estará
            disponible para asignarlo a cualquier sección.
          </p>
        </div>

        <div>
          <label>Tipo de docente</label>
          <select value={funcionCurso} onChange={(e) => setFuncionCurso(e.target.value)}>
            <option value="">Selecciona el tipo</option>
            <option value="Teorico" disabled={!funcionesPendientes.includes("Teorico")}>
              Teórico{!funcionesPendientes.includes("Teorico") ? " (ya asignado)" : ""}
            </option>
            <option value="Practico" disabled={!funcionesPendientes.includes("Practico")}>
              Práctico{!funcionesPendientes.includes("Practico") ? " (ya asignado)" : ""}
            </option>
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

        <button type="submit" disabled={seccionCompleta}>
          Guardar Asignación
        </button>
      </form>

      <h3>Registrar horario y aula de la sección</h3>
      <p style={{ color: "#aaa" }}>
        El horario y el aula pertenecen a la sección completa (no a un docente en particular): todos los
        docentes asignados a esta oferta académica comparten el mismo bloque de horario y aula/enlace
        virtual.
      </p>

      {asignaciones && asignaciones.horarios.length > 0 && (
        <table style={{ marginBottom: 12 }}>
          <thead>
            <tr>
              <th>Día</th>
              <th>Inicio</th>
              <th>Fin</th>
              <th>Aula / enlace</th>
            </tr>
          </thead>
          <tbody>
            {asignaciones.horarios.map((h) => (
              <tr key={h.id}>
                <td>{h.dia}</td>
                <td>{h.hora_inicio}</td>
                <td>{h.hora_fin}</td>
                <td>{h.aula}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

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
