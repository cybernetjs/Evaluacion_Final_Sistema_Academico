import { useEffect, useState } from "react";
import { solicitarDocumento, misSolicitudes, urlDescargarCertificadoEmitido } from "../servicios/certificados.servicio";

const TIPOS_DOCUMENTO = [
  "Constancia de Estudios",
  "Certificado de Estudios",
  "Constancia de Tercio Superior",
];

const EXTENSIONES_PERMITIDAS = ["pdf", "jpg", "jpeg", "png"];
const TAMANO_MAXIMO_BYTES = 5 * 1024 * 1024;

export default function CertificadosSolicitar() {
  const [tipo, setTipo] = useState("");
  const [archivo, setArchivo] = useState(null);
  const [errorArchivo, setErrorArchivo] = useState(null);
  const [tocoTipo, setTocoTipo] = useState(false);
  const [tocoArchivo, setTocoArchivo] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [respuesta, setRespuesta] = useState(null);
  const [error, setError] = useState(null);
  const [solicitudes, setSolicitudes] = useState([]);

  useEffect(() => {
    cargarSolicitudes();
  }, []);

  async function cargarSolicitudes() {
    const { data, error } = await misSolicitudes();
    if (!error) setSolicitudes(data);
  }

  function manejarSeleccionArchivo(e) {
    const seleccionado = e.target.files[0];
    setErrorArchivo(null);
    setArchivo(null);

    if (!seleccionado) return;

    const extension = seleccionado.name.split(".").pop().toLowerCase();
    if (!EXTENSIONES_PERMITIDAS.includes(extension)) {
      setErrorArchivo("Formato no permitido. Solo se aceptan PDF, JPEG o PNG.");
      return;
    }
    if (seleccionado.size === 0) {
      setErrorArchivo("El archivo está vacío.");
      return;
    }
    if (seleccionado.size > TAMANO_MAXIMO_BYTES) {
      setErrorArchivo("El archivo supera el tamaño máximo permitido de 5 MB.");
      return;
    }

    setArchivo(seleccionado);
  }

  const formularioValido = tipo !== "" && archivo !== null && !errorArchivo;

  async function manejarEnvio(evento) {
    evento.preventDefault();
    setTocoTipo(true);
    setTocoArchivo(true);
    setRespuesta(null);
    setError(null);

    if (!formularioValido) return;

    setEnviando(true);
    const { data, error } = await solicitarDocumento(tipo, archivo);
    setEnviando(false);

    if (error) {
      setError(error);
      return;
    }

    setRespuesta(data);
    setTipo("");
    setArchivo(null);
    setTocoTipo(false);
    setTocoArchivo(false);
    cargarSolicitudes();
  }

  return (
    <div className="contenedor">
      <h2>Solicitar documento oficial</h2>

      <form onSubmit={manejarEnvio}>
        <div>
          <label>Tipo de documento</label>
          <select
            value={tipo}
            onChange={(e) => setTipo(e.target.value)}
            onBlur={() => setTocoTipo(true)}
            style={{ borderColor: tocoTipo && tipo === "" ? "#ff6b6b" : undefined, borderWidth: tocoTipo && tipo === "" ? 2 : undefined }}
          >
            <option value="">Selecciona un tipo</option>
            {TIPOS_DOCUMENTO.map((opcion) => (
              <option key={opcion} value={opcion}>
                {opcion}
              </option>
            ))}
          </select>
        </div>

        <div style={{ marginTop: 12 }}>
          <label>Sustento de pago (PDF, JPEG o PNG, máx. 5 MB)</label>
          <input
            type="file"
            accept=".pdf,.jpg,.jpeg,.png"
            onChange={manejarSeleccionArchivo}
            onBlur={() => setTocoArchivo(true)}
            style={{
              borderColor: (errorArchivo || (tocoArchivo && !archivo)) ? "#ff6b6b" : undefined,
              borderWidth: (errorArchivo || (tocoArchivo && !archivo)) ? 2 : undefined,
            }}
          />
          {errorArchivo && <p style={{ color: "#ff6b6b" }}>{errorArchivo}</p>}
          {archivo && !errorArchivo && <p style={{ color: "#8fd18f" }}>{archivo.name}</p>}
        </div>

        <button type="submit" disabled={!formularioValido || enviando} style={{ marginTop: 12 }}>
          {enviando ? "Enviando..." : "Enviar Solicitud"}
        </button>
      </form>

      {respuesta && (
        <div style={{ marginTop: 16 }}>
          <p style={{ color: "green" }}>{respuesta.mensaje}</p>
          <p>Ticket: <strong>{respuesta.ticket_codigo}</strong> — Estado: {respuesta.estado}</p>
        </div>
      )}
      {error && <p style={{ color: "red", marginTop: 16 }}>{error}</p>}

      <h3 style={{ marginTop: 32 }}>Mis solicitudes</h3>
      <table>
        <thead>
          <tr>
            <th>Ticket</th>
            <th>Tipo</th>
            <th>Fecha</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {solicitudes.length > 0 ? (
            solicitudes.map((s) => (
              <tr key={s.id}>
                <td>{s.ticket_codigo}</td>
                <td>{s.tipo}</td>
                <td>{new Date(s.fecha_creacion).toLocaleDateString()}</td>
                <td>
                  {s.estado}
                  {s.estado === "Rechazado" && s.motivo_rechazo && (
                    <span style={{ color: "#ff6b6b" }}> — {s.motivo_rechazo}</span>
                  )}
                  {s.estado === "Emitido" && (
                    <a
                      href={urlDescargarCertificadoEmitido(s.id)}
                      target="_blank"
                      rel="noreferrer"
                      style={{ marginLeft: 8 }}
                    >
                      Descargar
                    </a>
                  )}
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="4">No has enviado solicitudes todavía.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
