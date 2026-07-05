import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import {
  autorizarCertificado,
  emitirCertificado,
  listarSolicitudes,
  urlQrCertificado,
  verificarCertificado,
} from "../servicios/certificados.servicio";

export default function CertificadosListar() {
  const { usuario } = useAuth();
  const [certificados, setCertificados] = useState([]);
  const [codigo, setCodigo] = useState("");
  const [verificacion, setVerificacion] = useState(null);
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    cargarSolicitudes();
  }, []);

  async function cargarSolicitudes() {
    setCargando(true);
    const { data, error } = await listarSolicitudes();
    setCargando(false);
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
      <p>Autoriza, emite y verifica certificados. El código de verificación aparece cuando el documento ya fue emitido.</p>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      <form onSubmit={manejarVerificacion}>
        <div>
          <label>Código de verificación</label>
          <input
            value={codigo}
            onChange={(e) => setCodigo(e.target.value)}
            placeholder="Pega aquí el código que aparece al emitir el certificado"
          />
        </div>
        <button type="submit">Buscar certificado</button>
      </form>

      <p>El código de verificación es un identificador único generado automáticamente. No se escribe manualmente al crear el certificado, se copia desde el documento emitido o desde la columna de la tabla.</p>

      {verificacion && (
        <ul>
          <li>Válido: {verificacion.valido ? "Sí" : "No"}</li>
          <li>Tipo: {verificacion.tipo}</li>
          <li>Estudiante: {verificacion.estudiante_id}</li>
        </ul>
      )}

      {cargando ? (
        <p>Cargando certificados...</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Estudiante</th>
              <th>Tipo</th>
              <th>Código</th>
              <th>Autorizado</th>
              <th>Emitido</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {certificados.length > 0 ? (
              certificados.map((certificado) => (
                <tr key={certificado.id}>
                  <td>{certificado.id}</td>
                  <td>{certificado.estudiante_id}</td>
                  <td>{certificado.tipo}</td>
                  <td>{certificado.codigo_verificacion || "Pendiente"}</td>
                  <td>{certificado.autorizado ? "Sí" : "No"}</td>
                  <td>{certificado.emitido ? "Sí" : "No"}</td>
                  <td>
                    {usuario?.rol === "direccion" && !certificado.autorizado && !certificado.emitido && (
                      <button type="button" onClick={() => manejarAutorizar(certificado.id)}>Autorizar</button>
                    )}
                    {usuario?.rol === "administrador" && certificado.autorizado && !certificado.emitido && (
                      <button type="button" onClick={() => manejarEmitir(certificado.id)}>Emitir</button>
                    )}
                    {certificado.codigo_verificacion && (
                      <a href={urlQrCertificado(certificado.codigo_verificacion)} target="_blank" rel="noreferrer">
                        QR
                      </a>
                    )}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7">No hay certificados registrados.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}