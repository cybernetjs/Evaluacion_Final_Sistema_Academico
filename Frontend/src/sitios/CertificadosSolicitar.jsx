import { useState } from "react";
import { solicitarCertificado } from "../servicios/certificados.servicio";

export default function CertificadosSolicitar() {
  const [tipo, setTipo] = useState("");
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
      <p>Elige el tipo de documento que necesitas registrar.</p>

      <form onSubmit={manejarEnvio}>
        <div>
          <label>Tipo de certificado</label>
          <input value={tipo} onChange={(e) => setTipo(e.target.value)} required />
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