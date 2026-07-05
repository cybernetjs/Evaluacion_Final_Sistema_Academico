import { useState, useEffect } from "react";
import {
  solicitarMatricula,
  listarPeriodos,
  urlDescargarFicha,
} from "../servicios/matricula.servicio";

export default function SolicitarMatricula() {
  const [periodos, setPeriodos] = useState([]);
  const [periodoAcademicoId, setPeriodoAcademicoId] = useState("");
  const [semestreId, setSemestreId] = useState("");
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);
  const [ultimaMatriculaId, setUltimaMatriculaId] = useState(null);

  useEffect(() => {
    cargarPeriodos();
  }, []);

  async function cargarPeriodos() {
    const { data, error } = await listarPeriodos();
    if (!error) {
      setPeriodos(data);
    }
  }

  async function manejarEnvio(evento) {
    evento.preventDefault();
    setMensaje(null);
    setError(null);

    const { data, error } = await solicitarMatricula({
      periodo_academico_id: Number(periodoAcademicoId),
      semestre_id: Number(semestreId),
    });

    if (error) {
      setError(error);
      return;
    }

    setMensaje(`Solicitud registrada correctamente. N° de matrícula: ${data.id}`);
    setUltimaMatriculaId(data.id);
  }

  async function manejarDescargaFicha() {
    const token = localStorage.getItem("token");
    const respuesta = await fetch(urlDescargarFicha(ultimaMatriculaId), {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!respuesta.ok) {
      setError("No se pudo descargar la ficha");
      return;
    }

    const blob = await respuesta.blob();
    const url = window.URL.createObjectURL(blob);
    const enlace = document.createElement("a");
    enlace.href = url;
    enlace.download = `ficha_matricula_${ultimaMatriculaId}.pdf`;
    enlace.click();
    window.URL.revokeObjectURL(url);
  }

  return (
    <div>
      <h2>Solicitar matrícula</h2>
      <form onSubmit={manejarEnvio}>
        <div>
          <label>Periodo académico</label>
          <select
            value={periodoAcademicoId}
            onChange={(e) => setPeriodoAcademicoId(e.target.value)}
            required
          >
            <option value="">Selecciona un periodo</option>
            {periodos.map((p) => (
              <option key={p.id} value={p.id}>
                {p.nombre}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label>Semestre</label>
          <input
            type="number"
            value={semestreId}
            onChange={(e) => setSemestreId(e.target.value)}
            required
          />
        </div>
        <button type="submit">Solicitar matrícula</button>
      </form>
      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {ultimaMatriculaId && (
        <button onClick={manejarDescargaFicha}>Descargar ficha (PDF)</button>
      )}
    </div>
  );
}