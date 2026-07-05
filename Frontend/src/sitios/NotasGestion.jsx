import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import {
  indicadoresAcademicos,
  listarNotas,
  obtenerNotasMatricula,
  validarActas,
} from "../servicios/notas.servicio";

export default function NotasGestion() {
  const { usuario } = useAuth();
  const [notas, setNotas] = useState([]);
  const [matriculaId, setMatriculaId] = useState("");
  const [consulta, setConsulta] = useState([]);
  const [actas, setActas] = useState(null);
  const [indicadores, setIndicadores] = useState(null);
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarNotas();
  }, []);

  async function cargarNotas() {
    const { data, error } = await listarNotas();
    if (!error) {
      setNotas(data);
    }
  }

  async function manejarConsulta(evento) {
    evento.preventDefault();
    setMensaje(null);
    setError(null);

    const { data, error } = await obtenerNotasMatricula(matriculaId);

    if (error) {
      setError(error);
      return;
    }

    setConsulta(data);
  }

  async function manejarValidarActas() {
    setMensaje(null);
    setError(null);
    const { data, error } = await validarActas();

    if (error) {
      setError(error);
      return;
    }

    setActas(data);
    setMensaje(data.mensaje);
  }

  async function manejarIndicadores() {
    setMensaje(null);
    setError(null);
    const { data, error } = await indicadoresAcademicos();

    if (error) {
      setError(error);
      return;
    }

    setIndicadores(data);
  }

  return (
    <div className="contenedor">
      <h2>Gestión de notas</h2>
      <p>Revisa el consolidado de notas, consulta indicadores y, si eres administrador, valida actas.</p>

      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "16px" }}>
        {usuario?.rol === "administrador" && (
          <button type="button" onClick={manejarValidarActas}>Validar actas</button>
        )}
        {(usuario?.rol === "administrador" || usuario?.rol === "direccion") && (
          <button type="button" onClick={manejarIndicadores}>Ver indicadores</button>
        )}
      </div>

      <form onSubmit={manejarConsulta}>
        <div>
          <label>ID de matrícula</label>
          <input type="number" value={matriculaId} onChange={(e) => setMatriculaId(e.target.value)} required />
        </div>
        <button type="submit">Consultar matrícula</button>
      </form>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {actas && (
        <ul>
          <li>Total de cursos matriculados: {actas.total_cursos_matriculados}</li>
          <li>Con nota registrada: {actas.con_nota_registrada}</li>
          <li>Pendientes de nota: {actas.pendientes_de_nota}</li>
        </ul>
      )}

      {indicadores && (
        <ul>
          <li>Promedio general: {indicadores.promedio_general ?? "Sin datos"}</li>
          <li>Total evaluados: {indicadores.total_evaluados}</li>
        </ul>
      )}

      <h3>Consolidado general</h3>
      <p>Si todavía no se registran notas, esta tabla se mostrará vacía hasta que el docente ingrese calificaciones.</p>
      <table>
        <thead>
          <tr>
            <th>Matrícula</th>
            <th>Oferta</th>
            <th>Parcial</th>
            <th>Final</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {notas.map((nota) => (
            <tr key={`${nota.matricula_id}-${nota.oferta_academica_id}`}>
              <td>{nota.matricula_id}</td>
              <td>{nota.oferta_academica_id}</td>
              <td>{nota.nota_parcial ?? "-"}</td>
              <td>{nota.nota_final ?? "-"}</td>
              <td>{nota.estado_curso_id}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Consulta por matrícula</h3>
      <p>Ingresa el número de matrícula para ver solo sus cursos y notas.</p>
      <table>
        <thead>
          <tr>
            <th>Oferta</th>
            <th>Parcial</th>
            <th>Final</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {consulta.map((nota, index) => (
            <tr key={`${nota.oferta_academica_id}-${index}`}>
              <td>{nota.oferta_academica_id}</td>
              <td>{nota.nota_parcial ?? "-"}</td>
              <td>{nota.nota_final ?? "-"}</td>
              <td>{nota.estado_curso_id}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}