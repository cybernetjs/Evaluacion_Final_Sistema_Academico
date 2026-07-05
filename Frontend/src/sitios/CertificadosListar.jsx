import { useEffect, useState } from "react";
import {
  autorizarCertificado,
  emitirCertificado,
  listarSolicitudes,
  urlQrCertificado,
  verificarCertificado,
} from "../servicios/certificados.servicio";

export default function CertificadosListar() {
  const [certificados, setCertificados] = useState([]);
  const [codigo, setCodigo] = useState("");
  const [verificacion, setVerificacion] = useState(null);
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarSolicitudes();
  }, []);

  async function cargarSolicitudes() {
    const { data, error } = await listarSolicitudes();
    if (error) {
      setError(error);
      return;
    }

    setCertificados(data);
  }

  async function manejarAutorizar(id) {
    setMensaje(null);
    setError(null);
    const { data, error } = await autorizarCertificado(id);

    if (error) {
      setError(error);
      return;
    }

    setMensaje(data.mensaje);
    cargarSolicitudes();
  }

  async function manejarEmitir(id) {
    setMensaje(null);
    setError(null);
    const { data, error } = await emitirCertificado(id);

    if (error) {
      setError(error);
      return;
    }

    setMensaje(data.mensaje);
    cargarSolicitudes();
  }

  async function manejarVerificacion(evento) {
    evento.preventDefault();
    setMensaje(null);
    setError(null);
    const { data, error } = await verificarCertificado(codigo);

    if (error) {
      setError(error);
      setVerificacion(null);
      return;
    }

    setVerificacion(data);
  }

  return (
    <div className="contenedor">
      <h2>Certificados y documentos</h2>
      <p>Autoriza, emite y verifica certificados registrados por los estudiantes.</p>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      <form onSubmit={manejarVerificacion}>
        <div>
          <label>Código de verificación</label>
          <input value={codigo} onChange={(e) => setCodigo(e.target.value)} />
        </div>
        <button type="submit">Verificar certificado</button>
      </form>

      {verificacion && (
        <ul>
          <li>Válido: {verificacion.valido ? "Sí" : "No"}</li>
          <li>Tipo: {verificacion.tipo}</li>
          <li>Estudiante: {verificacion.estudiante_id}</li>
        </ul>
      )}

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Estudiante</th>
            <th>Tipo</th>
            <th>Autorizado</th>
            <th>Emitido</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {certificados.map((certificado) => (
            <tr key={certificado.id}>
              <td>{certificado.id}</td>
              <td>{certificado.estudiante_id}</td>
              <td>{certificado.tipo}</td>
              <td>{certificado.autorizado ? "Sí" : "No"}</td>
              <td>{certificado.emitido ? "Sí" : "No"}</td>
              <td>
                <button onClick={() => manejarAutorizar(certificado.id)}>Autorizar</button>
                <button onClick={() => manejarEmitir(certificado.id)}>Emitir</button>
                {certificado.codigo_verificacion && (
                  <a href={urlQrCertificado(certificado.codigo_verificacion)} target="_blank" rel="noreferrer">
                    QR
                  </a>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}