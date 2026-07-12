import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import {
  bandeja,
  detalleExpediente,
  obtenerComprobanteBlobUrl,
  aprobarTramite,
  rechazarTramite,
  firmarCertificados,
  notificarSolicitud,
  urlDescargarCertificadoEmitido,
  verificarCertificado,
} from "../../servicios/certificados.servicio";

export default function CertificadosListar() {
  const { usuario } = useAuth();
  const [solicitudes, setSolicitudes] = useState([]);
  const [total, setTotal] = useState(0);
  const [filtroEstado, setFiltroEstado] = useState("");
  const [pagina, setPagina] = useState(1);
  const porPagina = 10;

  const [seleccionada, setSeleccionada] = useState(null);
  const [expediente, setExpediente] = useState(null);
  const [comprobanteUrl, setComprobanteUrl] = useState(null);
  const [tramiteARechazar, setTramiteARechazar] = useState(null);
  const [motivoRechazo, setMotivoRechazo] = useState("");

  const [seleccionParaFirma, setSeleccionParaFirma] = useState([]);
  const [mostrarConfirmacionFirma, setMostrarConfirmacionFirma] = useState(false);
  const [firmando, setFirmando] = useState(false);
  const [resultadosFirma, setResultadosFirma] = useState(null);

  const [codigo, setCodigo] = useState("");
  const [verificacion, setVerificacion] = useState(null);

  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [notificando, setNotificando] = useState(false);
  const [textoSugerido, setTextoSugerido] = useState(null);

  useEffect(() => {
    cargarBandeja();
  }, [filtroEstado, pagina]);

  async function cargarBandeja() {
    setCargando(true);
    const { data, error } = await bandeja({ estado: filtroEstado, pagina, porPagina });
    setCargando(false);
    if (error) {
      setError(error);
      return;
    }
    setSolicitudes(data.solicitudes);
    setTotal(data.total);
    setSeleccionParaFirma([]);
  }

  async function abrirExpediente(sol) {
    setSeleccionada(sol);
    setExpediente(null);
    setError(null);
    setTextoSugerido(null);
    limpiarComprobante();

    const { data, error } = await detalleExpediente(sol.id);
    if (error) {
      setError(error);
      setSeleccionada(null);
      return;
    }
    setExpediente(data);

    if (data.comprobante_disponible) {
      const resultado = await obtenerComprobanteBlobUrl(sol.id);
      if (!resultado.error) setComprobanteUrl(resultado.data);
    }
  }

  function limpiarComprobante() {
    setComprobanteUrl((actual) => {
      if (actual) URL.revokeObjectURL(actual);
      return null;
    });
  }

  function cerrarExpediente() {
    setSeleccionada(null);
    limpiarComprobante();
  }

  async function manejarAprobar(id) {
    setMensaje(null);
    setError(null);
    const { data, error } = await aprobarTramite(id);
    if (error) {
      setError(error);
      return;
    }
    setMensaje(data.mensaje);
    cerrarExpediente();
    cargarBandeja();
  }

  async function confirmarRechazo() {
    setMensaje(null);
    setError(null);
    const { data, error } = await rechazarTramite(tramiteARechazar.id, motivoRechazo);
    setTramiteARechazar(null);
    setMotivoRechazo("");

    if (error) {
      setError(error);
      return;
    }
    setMensaje(data.mensaje);
    cerrarExpediente();
    cargarBandeja();
  }

  async function manejarNotificar(certificadoId) {
    setNotificando(true);
    setMensaje(null);
    setError(null);
    setTextoSugerido(null);

    const { data, error } = await notificarSolicitud(certificadoId);
    setNotificando(false);

    if (error) {
      setError(error);
      return;
    }

    setMensaje(data.mensaje);
    setTextoSugerido({
      correo: data.correo_estudiante,
      asunto: data.asunto_sugerido,
      cuerpo: data.cuerpo_sugerido,
    });

    if (seleccionada?.id === certificadoId) {
      const resultado = await detalleExpediente(certificadoId);
      if (!resultado.error) setExpediente(resultado.data);
    }
  }

  function alternarSeleccionFirma(id) {
    setSeleccionParaFirma((actuales) =>
      actuales.includes(id) ? actuales.filter((item) => item !== id) : [...actuales, id]
    );
  }

  async function confirmarFirma() {
    setMostrarConfirmacionFirma(false);
    setFirmando(true);
    setMensaje(null);
    setError(null);

    const { data, error } = await firmarCertificados(seleccionParaFirma);
    setFirmando(false);

    if (error) {
      setError(error);
      return;
    }

    setResultadosFirma(data.resultados);
    setMensaje("Proceso de firma completado");
    cargarBandeja();
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

  const totalPaginas = Math.max(1, Math.ceil(total / porPagina));
  const esDireccion = usuario?.rol === "direccion";

  return (
    <div className="contenedor">
      <h2>Bandeja de Solicitudes Documentales</h2>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <select value={filtroEstado} onChange={(e) => { setFiltroEstado(e.target.value); setPagina(1); }}>
          <option value="">Todos los estados</option>
          <option value="Pendiente de Validación">Pendiente de Validación</option>
          <option value="Apto para Firma">Apto para Firma</option>
          <option value="Rechazado">Rechazado</option>
          <option value="Emitido">Emitido</option>
        </select>
      </div>

      {cargando ? (
        <p>Cargando...</p>
      ) : (
        <>
          <table>
            <thead>
              <tr>
                {esDireccion && <th></th>}
                <th>Ticket</th>
                <th>Estudiante</th>
                <th>Tipo</th>
                <th>Fecha</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {solicitudes.length > 0 ? (
                solicitudes.map((s) => (
                  <tr key={s.id}>
                    {esDireccion && (
                      <td>
                        {s.estado === "Apto para Firma" && (
                          <input
                            type="checkbox"
                            checked={seleccionParaFirma.includes(s.id)}
                            onChange={() => alternarSeleccionFirma(s.id)}
                          />
                        )}
                      </td>
                    )}
                    <td>{s.ticket_codigo}</td>
                    <td>{s.estudiante_nombre}</td>
                    <td>{s.tipo}</td>
                    <td>{new Date(s.fecha_creacion).toLocaleDateString()}</td>
                    <td>{s.estado}</td>
                    <td>
                      <button type="button" onClick={() => abrirExpediente(s)}>
                        Ver expediente
                      </button>
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
                  <td colSpan={esDireccion ? "7" : "6"}>No hay solicitudes en este estado.</td>
                </tr>
              )}
            </tbody>
          </table>

          {esDireccion && (
            <div style={{ marginTop: 12 }}>
              <button
                type="button"
                disabled={seleccionParaFirma.length === 0 || firmando}
                onClick={() => setMostrarConfirmacionFirma(true)}
              >
                {firmando ? "Firmando..." : `Firmar y emitir seleccionados (${seleccionParaFirma.length})`}
              </button>
            </div>
          )}

          {resultadosFirma && (
            <ul style={{ marginTop: 12 }}>
              {resultadosFirma.map((r) => (
                <li key={r.id} style={{ color: r.estado === "firmado" ? "#8fd18f" : "#ff6b6b" }}>
                  Certificado {r.id}: {r.estado === "firmado" ? "emitido correctamente" : r.detalle}
                </li>
              ))}
            </ul>
          )}

          <div style={{ display: "flex", gap: 8, marginTop: 12, alignItems: "center" }}>
            <button type="button" onClick={() => setPagina((p) => Math.max(1, p - 1))} disabled={pagina <= 1}>
              Anterior
            </button>
            <span>Página {pagina} de {totalPaginas}</span>
            <button type="button" onClick={() => setPagina((p) => Math.min(totalPaginas, p + 1))} disabled={pagina >= totalPaginas}>
              Siguiente
            </button>
          </div>
        </>
      )}

      {verificacion && !verificacion.valido && (
        <div
          style={{
            marginTop: 12,
            padding: 16,
            borderRadius: 8,
            background: "rgba(255, 0, 0, 0.12)",
            border: "1px solid #ff6b6b",
            color: "#ff6b6b",
          }}
        >
          {verificacion.mensaje}
        </div>
      )}
      {verificacion && verificacion.valido && (
        <div
          style={{
            marginTop: 12,
            padding: 16,
            borderRadius: 8,
            background: "rgba(0, 200, 0, 0.10)",
            border: "1px solid #8fd18f",
          }}
        >
          <p style={{ color: "#8fd18f", fontWeight: "bold" }}>Válido / Fidedigno</p>
          <ul>
            <li>Estudiante: {verificacion.estudiante_nombre}</li>
            <li>Tipo de documento: {verificacion.tipo}</li>
            <li>Fecha de emisión: {verificacion.fecha_emision ? new Date(verificacion.fecha_emision).toLocaleDateString() : "-"}</li>
            <li>Hash del documento: {verificacion.hash_documento}</li>
          </ul>
          <a
            href={urlDescargarCertificadoEmitido(verificacion.certificado_id)}
            target="_blank"
            rel="noreferrer"
          >
            Ver vista previa oficial
          </a>
        </div>
      )}

      {seleccionada && (
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
          onClick={cerrarExpediente}
        >
          <div
            style={{
              background: "#1e1e1e",
              border: "1px solid #6b6bff",
              borderRadius: 8,
              padding: 20,
              maxWidth: 700,
              width: "100%",
              display: "flex",
              gap: 20,
              maxHeight: "80vh",
              overflow: "auto",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ flex: 1 }}>
              <h4>Expediente — {seleccionada.ticket_codigo}</h4>
              {expediente ? (
                <>
                  <p>
                    {expediente.estudiante.nombres} {expediente.estudiante.apellido_paterno}{" "}
                    {expediente.estudiante.apellido_materno}
                  </p>
                  <p>Especialidad: {expediente.estudiante.especialidad}</p>
                  <p>Tipo de documento: {expediente.tipo}</p>
                  <p>Estado actual: {expediente.estado}</p>
                  {expediente.estado === "Emitido" ? (
                    <p>Código de verificación: <strong>{expediente.codigo_verificacion}</strong></p>
                  ) : (
                    <p style={{ color: "#aaa", fontSize: "0.9em" }}>
                      El código de verificación se genera recién cuando el trámite llega al estado
                      "Emitido" (después de ser aprobado por Administración y firmado por Dirección). Antes
                      de eso no existe ningún código válido para esta solicitud.
                    </p>
                  )}

                  <p>
                    Notificación al estudiante:{" "}
                    {expediente.notificado_en ? (
                      <span style={{ color: "#8fd18f" }}>
                        enviada el {new Date(expediente.notificado_en).toLocaleString()}
                      </span>
                    ) : (
                      <span style={{ color: "#aaa" }}>aún no se ha notificado</span>
                    )}
                  </p>
                  <p style={{ color: "#aaa", fontSize: "0.85em" }}>
                    El sistema no envía correos por su cuenta: este botón solo marca la solicitud como
                    atendida y te da un texto sugerido para que tú se lo copies y envíes al estudiante por
                    tu propio correo.
                  </p>
                  <button
                    type="button"
                    onClick={() => manejarNotificar(seleccionada.id)}
                    disabled={notificando}
                  >
                    {notificando
                      ? "Marcando..."
                      : expediente.notificado_en
                      ? "Marcar como notificado nuevamente"
                      : "Marcar solicitud como atendida / notificada"}
                  </button>

                  {textoSugerido && (
                    <div
                      style={{
                        marginTop: 8,
                        padding: 12,
                        border: "1px solid #6b6bff",
                        borderRadius: 6,
                        fontSize: "0.9em",
                      }}
                    >
                      <p>Para: {textoSugerido.correo || "el estudiante no tiene correo institucional registrado"}</p>
                      <p>Asunto: {textoSugerido.asunto}</p>
                      <p style={{ whiteSpace: "pre-wrap" }}>{textoSugerido.cuerpo}</p>
                    </div>
                  )}
                  <p>
                    Deuda activa:{" "}
                    <span style={{ color: expediente.estudiante.tiene_deuda_activa ? "#ff6b6b" : "#8fd18f" }}>
                      {expediente.estudiante.tiene_deuda_activa ? "Sí" : "No"}
                    </span>
                  </p>
                  <p>
                    Sanción activa:{" "}
                    <span style={{ color: expediente.estudiante.tiene_sancion_activa ? "#ff6b6b" : "#8fd18f" }}>
                      {expediente.estudiante.tiene_sancion_activa ? "Sí" : "No"}
                    </span>
                  </p>
                  <p>Créditos aprobados acumulados: {expediente.expediente_academico.creditos_aprobados_acumulados}</p>
                  <p>Promedio ponderado acumulado: {expediente.expediente_academico.promedio_ponderado_acumulado ?? "Sin datos"}</p>

                  {expediente.estado === "Pendiente de Validación" && !esDireccion && (
                    <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
                      <button type="button" onClick={() => manejarAprobar(seleccionada.id)}>
                        Aprobar y Derivar
                      </button>
                      <button type="button" onClick={() => setTramiteARechazar(seleccionada)}>
                        Rechazar Trámite
                      </button>
                    </div>
                  )}
                </>
              ) : (
                <p>Cargando expediente...</p>
              )}
            </div>

            <div style={{ flex: 1 }}>
              <h4>Sustento de pago</h4>
              {expediente?.comprobante_disponible ? (
                comprobanteUrl ? (
                  <iframe
                    src={comprobanteUrl}
                    title="Comprobante de pago"
                    style={{ width: "100%", height: 300, border: "1px solid #444" }}
                  />
                ) : (
                  <p>Cargando comprobante...</p>
                )
              ) : (
                <p>No hay comprobante adjunto.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {tramiteARechazar && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0,0,0,0.6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1100,
          }}
          onClick={() => setTramiteARechazar(null)}
        >
          <div
            style={{ background: "#1e1e1e", border: "1px solid #ff6b6b", borderRadius: 8, padding: 20, maxWidth: 420 }}
            onClick={(e) => e.stopPropagation()}
          >
            <h4 style={{ marginTop: 0 }}>Rechazar trámite {tramiteARechazar.ticket_codigo}</h4>
            <label>Motivo del rechazo (obligatorio)</label>
            <textarea
              value={motivoRechazo}
              onChange={(e) => setMotivoRechazo(e.target.value)}
              rows={4}
              style={{ width: "100%", marginTop: 4, marginBottom: 12 }}
            />
            <div style={{ display: "flex", gap: 8 }}>
              <button type="button" onClick={confirmarRechazo} disabled={motivoRechazo.trim() === ""}>
                Confirmar rechazo
              </button>
              <button type="button" onClick={() => setTramiteARechazar(null)}>
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}

      {mostrarConfirmacionFirma && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0,0,0,0.6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1100,
          }}
          onClick={() => setMostrarConfirmacionFirma(false)}
        >
          <div
            style={{ background: "#1e1e1e", border: "1px solid #6b6bff", borderRadius: 8, padding: 20, maxWidth: 420 }}
            onClick={(e) => e.stopPropagation()}
          >
            <h4 style={{ marginTop: 0 }}>Confirmar firma digital</h4>
            <p>
              Vas a firmar y emitir {seleccionParaFirma.length} certificado(s). Esta acción generará el
              documento oficial definitivo y no podrá deshacerse. ¿Deseas continuar?
            </p>
            <div style={{ display: "flex", gap: 8 }}>
              <button type="button" onClick={confirmarFirma}>
                Confirmar y firmar
              </button>
              <button type="button" onClick={() => setMostrarConfirmacionFirma(false)}>
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
