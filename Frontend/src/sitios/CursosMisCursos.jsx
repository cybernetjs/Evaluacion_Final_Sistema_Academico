import { useEffect, useState } from "react";
import {
  cargarSilabo,
  misCursosAsignados,
  periodosHistoricosDocente,
  urlDescargarSilabo,
} from "../servicios/cursosDocentes.servicio";

const DIAS_CALENDARIO = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"];
const HORAS_CALENDARIO = Array.from({ length: 15 }, (_, i) => i + 7);

function horaANumero(texto) {
  if (!texto) return null;
  const [horas] = texto.split(":");
  return Number(horas);
}

export default function CursosMisCursos() {
  const [cursos, setCursos] = useState([]);
  const [periodos, setPeriodos] = useState([]);
  const [periodoSeleccionado, setPeriodoSeleccionado] = useState("");
  const [ofertaSeleccionada, setOfertaSeleccionada] = useState("");
  const [archivo, setArchivo] = useState(null);
  const [arrastrando, setArrastrando] = useState(false);
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    periodosHistoricosDocente().then((res) => {
      if (!res.error) setPeriodos(res.data);
    });
    cargarCursos();
  }, []);

  async function cargarCursos(periodoAcademicoId) {
    const { data, error } = await misCursosAsignados(periodoAcademicoId);
    if (error) {
      setError(error);
      setCursos([]);
      return;
    }

    setError(null);
    setCursos(data);
    if (data?.length && !ofertaSeleccionada) {
      setOfertaSeleccionada(String(data[0].oferta_academica_id));
    }
  }

  function manejarCambioPeriodo(valor) {
    setPeriodoSeleccionado(valor);
    cargarCursos(valor || undefined);
  }

  function validarArchivo(archivoElegido) {
    if (!archivoElegido) return;

    if (archivoElegido.type !== "application/pdf") {
      setError("Formato no válido. Solo se permiten documentos en formato PDF");
      setArchivo(null);
      return;
    }

    setError(null);
    setArchivo(archivoElegido);
  }

  function manejarSoltarArchivo(evento) {
    evento.preventDefault();
    setArrastrando(false);
    const archivoElegido = evento.dataTransfer.files?.[0];
    validarArchivo(archivoElegido);
  }

  async function manejarCargaSilabo(evento) {
    evento.preventDefault();
    setMensaje(null);

    if (!ofertaSeleccionada || !archivo) {
      setError("Debes elegir un curso y adjuntar un archivo PDF");
      return;
    }

    setCargando(true);
    const { data, error } = await cargarSilabo(ofertaSeleccionada, archivo);
    setCargando(false);

    if (error) {
      setError(error);
      return;
    }

    setError(null);
    setMensaje(data.mensaje);
    setArchivo(null);
    cargarCursos(periodoSeleccionado || undefined);
  }

  const cursoSeleccionadoInfo = cursos.find(
    (c) => String(c.oferta_academica_id) === ofertaSeleccionada
  );

  const bloquesCalendario = {};
  cursos.forEach((curso) => {
    curso.horario.forEach((h) => {
      const inicio = horaANumero(h.hora_inicio);
      const fin = horaANumero(h.hora_fin);
      if (inicio === null || fin === null) return;
      for (let hora = inicio; hora < fin; hora++) {
        const clave = `${h.dia_numero}-${hora}`;
        bloquesCalendario[clave] = `${curso.codigo_curso} (${h.aula || "sin aula"})`;
      }
    });
  });

  return (
    <div className="contenedor">
      <h2>Mi carga académica</h2>
      <p>Consulta tus cursos y secciones asignadas para el periodo académico.</p>

      <select value={periodoSeleccionado} onChange={(e) => manejarCambioPeriodo(e.target.value)}>
        <option value="">Periodo académico vigente</option>
        {periodos.map((p) => (
          <option key={p.id} value={p.id}>{p.nombre}</option>
        ))}
      </select>

      {error && <p style={{ color: "red" }}>{error}</p>}
      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}

      {cursos.length === 0 && !error && (
        <p>
          Aún no cuenta con asignaturas asignadas para el presente ciclo. Si considera que es un
          error, comuníquese con el Administrador.
        </p>
      )}

      {cursos.length > 0 && (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 12, marginBottom: 24 }}>
            {cursos.map((curso) => (
              <div
                key={curso.oferta_academica_id}
                style={{ border: "1px solid #444", borderRadius: 8, padding: 12 }}
              >
                <p style={{ margin: 0, fontWeight: "bold" }}>{curso.nombre_curso}</p>
                <p style={{ margin: "4px 0", opacity: 0.7 }}>{curso.codigo_curso} - Sección {curso.seccion}</p>
                <p style={{ margin: "2px 0" }}>Créditos: {curso.creditos}</p>
                <p style={{ margin: "2px 0" }}>Función: {curso.funcion_curso || "-"}</p>
                <p style={{ margin: "2px 0" }}>Horas semanales: {curso.horas_semanales ?? "-"}</p>
                <p
                  style={{
                    margin: "6px 0 0",
                    fontWeight: "bold",
                    color: curso.estado_silabo === "Silabo Cargado" ? "#2e7d32" : "#b7791f",
                  }}
                >
                  {curso.estado_silabo}
                </p>
              </div>
            ))}
          </div>

          <h3>Calendario semanal</h3>
          <table>
            <thead>
              <tr>
                <th>Hora</th>
                {DIAS_CALENDARIO.map((dia) => (
                  <th key={dia}>{dia}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {HORAS_CALENDARIO.map((hora) => (
                <tr key={hora}>
                  <td>{hora}:00</td>
                  {DIAS_CALENDARIO.map((_, indice) => {
                    const dia = indice + 1;
                    const clave = `${dia}-${hora}`;
                    const contenido = bloquesCalendario[clave];
                    return (
                      <td
                        key={clave}
                        style={contenido ? { backgroundColor: "rgba(107, 107, 255, 0.2)" } : undefined}
                      >
                        {contenido || ""}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>

          <h3>Sílabo del curso</h3>
          <select value={ofertaSeleccionada} onChange={(e) => setOfertaSeleccionada(e.target.value)}>
            {cursos.map((curso) => (
              <option key={curso.oferta_academica_id} value={curso.oferta_academica_id}>
                {curso.nombre_curso} - Sección {curso.seccion}
              </option>
            ))}
          </select>

          <div
            onDragOver={(e) => {
              e.preventDefault();
              setArrastrando(true);
            }}
            onDragLeave={() => setArrastrando(false)}
            onDrop={manejarSoltarArchivo}
            style={{
              border: `2px dashed ${arrastrando ? "#6b6bff" : "#666"}`,
              borderRadius: 8,
              padding: 24,
              textAlign: "center",
              margin: "12px 0",
            }}
          >
            <p>Arrastra aquí el archivo PDF del sílabo, o selecciónalo manualmente</p>
            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => validarArchivo(e.target.files?.[0] || null)}
            />
            {archivo && <p>Archivo listo: {archivo.name}</p>}
          </div>

          <button type="button" onClick={manejarCargaSilabo} disabled={cargando}>
            {cargando ? "Subiendo..." : cursoSeleccionadoInfo?.estado_silabo === "Silabo Cargado" ? "Actualizar sílabo" : "Cargar Sílabo"}
          </button>

          {cursoSeleccionadoInfo?.estado_silabo === "Silabo Cargado" && (
            <a
              href={urlDescargarSilabo(ofertaSeleccionada)}
              target="_blank"
              rel="noreferrer"
              style={{ marginLeft: 12 }}
            >
              Descargar / visualizar sílabo actual
            </a>
          )}
        </>
      )}
    </div>
  );
}
