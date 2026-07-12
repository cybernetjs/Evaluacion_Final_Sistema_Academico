import { useState } from "react";
import { registrarPago } from "../servicios/matriculaServicio";

const EXTENSIONES_PERMITIDAS = ["pdf", "jpg", "jpeg", "png"];
const TAMANO_MAXIMO_BYTES = 5 * 1024 * 1024;

export default function ModalRegistrarPago({ matricula, onCerrar, onExito }) {
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
      setErrorArchivo("Formato no permitido, solo se aceptan PDF, JPEG o PNG");
      return;
    }

    if (seleccionado.size > TAMANO_MAXIMO_BYTES) {
      setErrorArchivo("El archivo supera el tamano maximo permitido de 5 MB");
      return;
    }

    setArchivo(seleccionado);
  }

  async function manejarEnvio(e) {
    e.preventDefault();
    setError(null);

    if (!archivo) {
      setError("Adjunta el comprobante de pago");
      return;
    }

    setEnviando(true);
    const { data, error } = await registrarPago(matricula.id, archivo);
    setEnviando(false);

    if (error) {
      setError(error);
      return;
    }

    setConfirmado(true);
    onExito(data);
  }

  return (
    <div className="modal-fondo" onClick={onCerrar}>
      <form className="modal-caja" onSubmit={manejarEnvio} onClick={(e) => e.stopPropagation()}>
        <h3>Subir comprobante - Matricula #{matricula.id}</h3>

        <div className="campo">
          <label>Comprobante (PDF, JPEG o PNG, maximo 5 MB)</label>
          <input
            type="file"
            accept=".pdf,.jpg,.jpeg,.png"
            onChange={manejarSeleccionArchivo}
            disabled={confirmado}
          />
        </div>

        {errorArchivo && <p className="mensaje-error">{errorArchivo}</p>}
        {archivo && !errorArchivo && <p className="mensaje-exito">{archivo.name}</p>}
        {error && <p className="mensaje-error">{error}</p>}
        {confirmado && (
          <p className="mensaje-exito">
            Comprobante enviado. Administracion lo revisara y verificara.
          </p>
        )}

        <div>
          {!confirmado && (
            <button type="submit" disabled={enviando || !archivo || errorArchivo}>
              {enviando ? "Enviando..." : "Confirmar y registrar pago"}
            </button>
          )}
          <button type="button" className="secundario" onClick={onCerrar}>
            {confirmado ? "Cerrar" : "Cancelar"}
          </button>
        </div>
      </form>
    </div>
  );
}
