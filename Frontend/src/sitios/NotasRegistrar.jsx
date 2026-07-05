import { useEffect, useState } from "react";
import { listarEstadosCurso, registrarNota } from "../servicios/notas.servicio";

export default function NotasRegistrar() {
  const [matriculaId, setMatriculaId] = useState("");
  const [ofertaAcademicaId, setOfertaAcademicaId] = useState("");
  const [notaParcial, setNotaParcial] = useState("");
  const [notaFinal, setNotaFinal] = useState("");
  const [estadoCursoId, setEstadoCursoId] = useState("");
  const [estados, setEstados] = useState([]);
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarEstados();
  }, []);

  async function cargarEstados() {
    const { data, error } = await listarEstadosCurso();
    if (!error) {
      setEstados(data);
      if (data?.length && !estadoCursoId) {
        setEstadoCursoId(String(data[0].id));
      }
    }
  }

  async function manejarEnvio(evento) {
    evento.preventDefault();
    setMensaje(null);
    setError(null);

    const { data, error } = await registrarNota({
      matricula_id: Number(matriculaId),
      oferta_academica_id: Number(ofertaAcademicaId),
      nota_parcial: notaParcial === "" ? null : Number(notaParcial),
      nota_final: notaFinal === "" ? null : Number(notaFinal),
      estado_curso_id: Number(estadoCursoId),
    });

    if (error) {
      setError(error);
      return;
    }

    setMensaje(data.mensaje);
  }

  return (
    <div className="contenedor">
      <h2>Registrar notas</h2>
      <p>Ingresa las calificaciones parciales y finales de cada matrícula.</p>

      <form onSubmit={manejarEnvio}>
        <div>
          <label>Matrícula</label>
          <input type="number" value={matriculaId} onChange={(e) => setMatriculaId(e.target.value)} required />
        </div>
        <div>
          <label>Oferta académica</label>
          <input type="number" value={ofertaAcademicaId} onChange={(e) => setOfertaAcademicaId(e.target.value)} required />
        </div>
        <div>
          <label>Nota parcial</label>
          <input type="number" step="0.01" value={notaParcial} onChange={(e) => setNotaParcial(e.target.value)} />
        </div>
        <div>
          <label>Nota final</label>
          <input type="number" step="0.01" value={notaFinal} onChange={(e) => setNotaFinal(e.target.value)} />
        </div>
        <div>
          <label>Estado del curso</label>
          <select value={estadoCursoId} onChange={(e) => setEstadoCursoId(e.target.value)}>
            {estados.map((estado) => (
              <option key={estado.id} value={estado.id}>
                {estado.nombre}
              </option>
            ))}
          </select>
        </div>
        <button type="submit">Guardar nota</button>
      </form>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}