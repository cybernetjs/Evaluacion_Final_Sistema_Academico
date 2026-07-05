import { useState } from "react";
import { solicitarCertificado } from "../servicios/certificados.servicio";

const TIPOS_CERTIFICADO = [
  "Constancia de estudios",
  "Constancia de matrícula",
  "Certificado de notas",
  "Récord académico",
  "Constancia de egreso",
];

export default function CertificadosSolicitar() {
  const [tipo, setTipo] = useState(TIPOS_CERTIFICADO[0]);
  const [respuesta, setRespuesta] = useState(null);
  const [error, setError] = useState(null);

  async function manejarEnvio(evento) {
    evento.preventDefault();
    setRespuesta(null);
    setError(null);

    const { data, error } = await solicitarCertificado({ tipo });

    if (error) {
      setError(error);
      return;
    }

    setRespuesta(data);
    setTipo("");
  }

  return (
    <div className="contenedor">
      <h2>Solicitar certificado</h2>
      <p>Selecciona el documento que necesitas. Estos son los tipos disponibles en el sistema.</p>

      <form onSubmit={manejarEnvio}>
        <div>
          <label>Tipo de documento</label>
          <select value={tipo} onChange={(e) => setTipo(e.target.value)} required>
            {TIPOS_CERTIFICADO.map((opcion) => (
              <option key={opcion} value={opcion}>
                {opcion}
              </option>
            ))}
          </select>
        </div>
        <button type="submit">Solicitar</button>
      </form>

      {respuesta && (
        <ul>
          <li>Mensaje: {respuesta.mensaje}</li>
          <li>Solicitud: {respuesta.id}</li>
          <li>Tipo: {respuesta.tipo}</li>
        </ul>
      )}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}