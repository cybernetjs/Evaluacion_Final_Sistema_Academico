import { useEffect, useState } from "react";
import { analisisCohorte, listarAniosIngreso } from "../servicios/recordAcademicoServicio";
import { listarEspecialidades } from "../../administracion/servicios/administracionServicio";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";

const COLORES = ["#6b6bff", "#f2a154", "#4caf50"];

export default function AnalisisCohorte() {
  const [anios, setAnios] = useState([]);
  const [especialidades, setEspecialidades] = useState([]);
  const [especialidadId, setEspecialidadId] = useState("");
  const [aniosSeleccionados, setAniosSeleccionados] = useState([]);
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarCatalogos();
  }, []);

  async function cargarCatalogos() {
    const [resAnios, resEspecialidades] = await Promise.all([
      listarAniosIngreso(),
      listarEspecialidades(),
    ]);
    if (!resAnios.error) setAnios(resAnios.data);
    if (!resEspecialidades.error) setEspecialidades(resEspecialidades.data);
  }

  function alternarAnio(anio) {
    setAniosSeleccionados((actuales) => {
      if (actuales.includes(anio)) {
        return actuales.filter((a) => a !== anio);
      }
      if (actuales.length >= 3) {
        return actuales;
      }
      return [...actuales, anio];
    });
  }

  async function manejarAnalizar() {
    if (!especialidadId || aniosSeleccionados.length === 0) {
      setError("Selecciona un programa de estudios y al menos un año de ingreso");
      return;
    }

    const { data, error } = await analisisCohorte(especialidadId, aniosSeleccionados);
    if (error) {
      setError(error);
      setResultado(null);
      return;
    }

    setError(null);
    setResultado(data);
  }

  return (
    <div className="contenedor">
      <h2>Análisis por cohorte</h2>
      

      {error && <p style={{ color: "red" }}>{error}</p>}

      <div style={{ display: "flex", gap: 12, marginBottom: 12, flexWrap: "wrap" }}>
        <select value={especialidadId} onChange={(e) => setEspecialidadId(e.target.value)}>
          <option value="">Programa de estudios</option>
          {especialidades.map((e) => (
            <option key={e.id} value={e.id}>{e.nombre}</option>
          ))}
        </select>

        {anios.map((anio) => (
          <label key={anio} style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <input
              type="checkbox"
              checked={aniosSeleccionados.includes(anio)}
              onChange={() => alternarAnio(anio)}
            />
            {anio}
          </label>
        ))}

        <button type="button" onClick={manejarAnalizar}>Comparar</button>
      </div>

      {resultado && (
        <>
          <div style={{ display: "flex", gap: 16, marginBottom: 24, flexWrap: "wrap" }}>
            {resultado.cohortes.map((c) => (
              <div
                key={c.anio_ingreso}
                style={{
                  border: "1px solid #444",
                  borderRadius: 8,
                  padding: 16,
                  minWidth: 200,
                  backgroundColor: c.en_alerta ? "rgba(255, 0, 0, 0.12)" : undefined,
                }}
              >
                <p style={{ margin: 0, opacity: 0.7 }}>Cohorte {c.anio_ingreso}</p>
                <p style={{ margin: 0, fontSize: 22, fontWeight: "bold" }}>
                  {c.total_estudiantes} estudiantes
                </p>
                <p style={{ margin: "4px 0" }}>Promedio general: {c.promedio_general ?? "Sin datos"}</p>
                <p
                  style={{
                    margin: 0,
                    color: c.en_alerta ? "#c0392b" : undefined,
                    fontWeight: c.en_alerta ? "bold" : undefined,
                  }}
                >
                  Deserción: {c.tasa_desercion_porcentaje}%{c.en_alerta ? " - ALERTA" : ""}
                </p>
              </div>
            ))}
          </div>

          <h3>Evolución del promedio ponderado por semestre</h3>
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={resultado.serie_grafico}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="semestre" />
              <YAxis domain={[0, 20]} />
              <Tooltip />
              <Legend />
              {aniosSeleccionados.map((anio, indice) => (
                <Line
                  key={anio}
                  type="monotone"
                  dataKey={`cohorte_${anio}`}
                  name={`Cohorte ${anio}`}
                  stroke={COLORES[indice % COLORES.length]}
                  connectNulls
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </>
      )}
    </div>
  );
}
