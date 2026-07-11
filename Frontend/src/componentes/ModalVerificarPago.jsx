import { useState } from "react";
import { verificarPago } from "../servicios/matricula.servicio";

export default function ModalVerificarPago({ matricula, comprobanteUrl, cargandoComprobante, onCerrar, onExito }) {
  const [numeroOperacion, setNumeroOperacion] = useState("");
  const [fechaPago, setFechaPago] = useState("");
  const [monto, setMonto] = useState("");
  const [error, setError] = useState(null);
  const [enviando, setEnviando] = useState(false);

  async function manejarEnvio(e) {
    e.preventDefault();
    setError(null);

    if (!numeroOperacion || !fechaPago || !monto) {
      setError("Completa el número de operación, la fecha y el monto");
      return;
    }

    setEnviando(true);
    const { data, error } = await verificarPago(matricula.id, {
      numeroOperacion,
      fechaPago,
      monto,
    });
    setEnviando(false);

    if (error) {
      setError(error);
      return;
    }

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
      <div
        style={{ background: "#1e1e1e", border: "1px solid #6b6bff", borderRadius: 8, padding: 20, maxWidth: 460, width: "100%" }}
        onClick={(e) => e.stopPropagation()}
      >
        <h4 style={{ marginTop: 0 }}>Verificar pago — Matrícula #{matricula.id}</h4>

        <p style={{ fontWeight: "bold", marginBottom: 4 }}>Comprobante enviado por el estudiante</p>
        {cargandoComprobante && <p>Cargando comprobante...</p>}
        {!cargandoComprobante && comprobanteUrl && (
          <iframe
            src={comprobanteUrl}
            title="Comprobante de pago"
            style={{ width: "100%", height: 260, border: "1px solid #444", marginBottom: 12 }}
          />
        )}
        {!cargandoComprobante && !comprobanteUrl && (
          <p style={{ color: "#aaa", marginBottom: 12 }}>No hay comprobante disponible.</p>
        )}

        <form onSubmit={manejarEnvio}>
          <label>Número de Operación Bancaria</label>
          <input
            type="text"
            value={numeroOperacion}
            onChange={(e) => setNumeroOperacion(e.target.value)}
            style={{ width: "100%", marginBottom: 10 }}
          />

          <label>Fecha de Pago</label>
          <input
            type="date"
            value={fechaPago}
            onChange={(e) => setFechaPago(e.target.value)}
            style={{ width: "100%", marginBottom: 10 }}
          />

          <label>Monto Pagado</label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={monto}
            onChange={(e) => setMonto(e.target.value)}
            style={{ width: "100%", marginBottom: 10 }}
          />

          {error && <p style={{ color: "#ff6b6b" }}>{error}</p>}

          <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
            <button type="submit" disabled={enviando}>
              {enviando ? "Verificando..." : "Verificar pago"}
            </button>
            <button type="button" onClick={onCerrar}>
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
