import { useEffect, useState } from "react";
import {
  cargarSilabo,
  misCursosAsignados,
  urlDescargarSilabo,
} from "../servicios/cursosDocentes.servicio";

export default function CursosMisCursos() {
  const [cursos, setCursos] = useState([]);
  const [ofertaSeleccionada, setOfertaSeleccionada] = useState("");
  const [archivo, setArchivo] = useState(null);
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarCursos();
  }, []);

  async function cargarCursos() {
    const { data, error } = await misCursosAsignados();
    if (error) {
      setError(error);
      return;
    }

    setCursos(data);
    if (data?.length && !ofertaSeleccionada) {
      setOfertaSeleccionada(String(data[0].oferta_academica_id));
    }
  }

  async function manejarCargaSilabo(evento) {
    evento.preventDefault();
    setMensaje(null);
    setError(null);

    if (!ofertaSeleccionada || !archivo) {
      setError("Debes elegir una oferta y adjuntar un archivo");
      return;
    }

    const { data, error } = await cargarSilabo(ofertaSeleccionada, archivo);

    if (error) {
      setError(error);
      return;
    }

    setMensaje(data.mensaje);
    setArchivo(null);
  }

  return (
    <div className="contenedor">
      <h2>Mis cursos asignados</h2>
      <p>Desde aquí puedes ver tus cursos y subir el sílabo cuando corresponda.</p>

      <form onSubmit={manejarCargaSilabo}>
        <div>
          <label>Oferta académica</label>
          <select value={ofertaSeleccionada} onChange={(e) => setOfertaSeleccionada(e.target.value)}>
            <option value="">Selecciona una oferta</option>
            {cursos.map((curso) => (
              <option key={curso.oferta_academica_id} value={curso.oferta_academica_id}>
                {curso.curso_nombre} - Semestre {curso.semestre_id}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label>Archivo del sílabo</label>
          <input type="file" onChange={(e) => setArchivo(e.target.files?.[0] || null)} />
        </div>
        <button type="submit">Subir sílabo</button>
      </form>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      <table>
        <thead>
          <tr>
            <th>Curso</th>
            <th>Semestre</th>
            <th>Periodo</th>
            <th>Cupos</th>
            <th>Sílabo</th>
          </tr>
        </thead>
        <tbody>
          {cursos.map((curso) => (
            <tr key={curso.oferta_academica_id}>
              <td>{curso.curso_nombre}</td>
              <td>{curso.semestre_id}</td>
              <td>{curso.periodo_academico_id}</td>
              <td>{curso.cupos}</td>
              <td>
                <a href={urlDescargarSilabo(curso.oferta_academica_id)} target="_blank" rel="noreferrer">
                  Descargar
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}