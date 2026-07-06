import { useState } from "react";
import { registrarPago } from "../servicios/matricula.servicio";

const EXTENSIONES_PERMITIDAS = ["pdf", "jpg", "jpeg", "png"];
const TAMANO_MAXIMO_BYTES = 5 * 1024 * 1024;

export default function ModalRegistrarPago({ matricula, onCerrar, onExito }) {
  const [numeroOperacion, setNumeroOperacion] = useState("");
  const [fechaPago, setFechaPago] = useState("");
  const [monto, setMonto] = useState("");
  const [archivo, setArchivo] = useState(null);
  const [errorArchivo, setErrorArchivo] = useState(null);
  const [error, setError] = useState(null);
  const [enviando, setEnviando] = useState(false);
  const [confirmado, setConfirmado] = useState(false);

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

    if (seleccionado.size > TAMANO_MAXIMO_BYTES) {
      setErrorArchivo("El archivo supera el tamaño máximo permitido de 5 MB.");
      return;
    }

    setArchivo(seleccionado);
  }

  async function manejarEnvio(e) {
    e.preventDefault();
    setError(null);

    if (!numeroOperacion || !fechaPago || !monto || !archivo) {
      setError("Completa todos los campos y adjunta el comprobante");
      return;
    }

    setEnviando(true);
    const { data, error } = await registrarPago(matricula.id, {
      numeroOperacion,
      fechaPago,
      monto,
      archivo,
    });
    setEnviando(false);

    if (error) {
      setError(error);
      return;
    }

    setConfirmado(true);
    onExito(data);
  }

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: "rgba(0,0,0,0.5)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
      }}
      onClick={onCerrar}
    >
      <form
        onSubmit={manejarEnvio}
        style={{ background: "#1e1e1e", border: "1px solid #6b6bff", borderRadius: 8, padding: 20, maxWidth: 420, width: "100%" }}
        onClick={(e) => e.stopPropagation()}
      >
        <h4 style={{ marginTop: 0 }}>Registrar pago — Matrícula #{matricula.id}</h4>

        <label>Número de Operación Bancaria</label>
        <input
          type="text"
          value={numeroOperacion}
          onChange={(e) => setNumeroOperacion(e.target.value)}
          readOnly={confirmado}
          style={{ width: "100%", marginBottom: 10 }}
        />

        <label>Fecha de Pago</label>
        <input
          type="date"
          value={fechaPago}
          onChange={(e) => setFechaPago(e.target.value)}
          readOnly={confirmado}
          disabled={confirmado}
          style={{ width: "100%", marginBottom: 10 }}
        />

        <label>Monto Pagado</label>
        <input
          type="number"
          step="0.01"
          min="0"
          value={monto}
          onChange={(e) => setMonto(e.target.value)}
          readOnly={confirmado}
          style={{ width: "100%", marginBottom: 10 }}
        />

        <label>Comprobante (PDF, JPEG o PNG, máx. 5 MB)</label>
        <input
          type="file"
          accept=".pdf,.jpg,.jpeg,.png"
          onChange={manejarSeleccionArchivo}
          disabled={confirmado}
          style={{ width: "100%", marginBottom: 6 }}
        />
        {errorArchivo && <p style={{ color: "#ff6b6b", marginTop: 0 }}>{errorArchivo}</p>}
        {archivo && !errorArchivo && <p style={{ color: "#8fd18f", marginTop: 0 }}>{archivo.name}</p>}

        {error && <p style={{ color: "#ff6b6b" }}>{error}</p>}
        {confirmado && <p style={{ color: "#8fd18f" }}>Pago confirmado. El formulario ya no puede modificarse.</p>}

        <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
          {!confirmado && (
            <button type="submit" disabled={enviando || !archivo || errorArchivo}>
              {enviando ? "Registrando..." : "Confirmar y Registrar Pago"}
            </button>
          )}
          <button type="button" onClick={onCerrar}>
            {confirmado ? "Cerrar" : "Cancelar"}
          </button>
        </div>
      </form>
    </div>
  );
}
