import { useState } from "react";
import { verificarPago } from "../servicios/matriculaServicio";

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
      setError("Completa el numero de operacion, la fecha y el monto");
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
    <div className="modal-fondo" onClick={onCerrar}>
      <div className="modal-caja" onClick={(e) => e.stopPropagation()}>
        <h3>Verificar pago - Matricula #{matricula.id}</h3>

        <p>Comprobante enviado por el estudiante</p>
        {cargandoComprobante && <p>Cargando comprobante...</p>}
        {!cargandoComprobante && comprobanteUrl && (
          <iframe
            src={comprobanteUrl}
            title="Comprobante de pago"
            style={{ width: "100%", height: 240, border: "1px solid var(--linea)", marginBottom: 14 }}
          />
        )}
        {!cargandoComprobante && !comprobanteUrl && <p>No hay comprobante disponible</p>}

        <form onSubmit={manejarEnvio}>
          <div className="campo">
            <label>Numero de operacion bancaria</label>
            <input
              type="text"
              value={numeroOperacion}
              onChange={(e) => setNumeroOperacion(e.target.value)}
            />
          </div>

          <div className="campo">
            <label>Fecha de pago</label>
            <input
              type="date"
              value={fechaPago}
              onChange={(e) => setFechaPago(e.target.value)}
            />
          </div>

          <div className="campo">
            <label>Monto pagado</label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={monto}
              onChange={(e) => setMonto(e.target.value)}
            />
          </div>

          {error && <p className="mensaje-error">{error}</p>}

          <div>
            <button type="submit" disabled={enviando}>
              {enviando ? "Verificando..." : "Verificar pago"}
            </button>
            <button type="button" className="secundario" onClick={onCerrar}>
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
