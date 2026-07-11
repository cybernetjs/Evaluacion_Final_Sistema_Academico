import { useEffect, useState } from "react";
import { obtenerMatrizPermisos, actualizarMatrizPermisos } from "../servicios/administracion.servicio";

const ETIQUETAS_RECURSO = {
  matricula: "Matrícula",
  notas: "Notas",
  certificados: "Certificados",
  cursos_docentes: "Cursos y Docentes",
  administracion: "Administración",
  auditoria: "Auditoría",
  record_academico: "Récord Académico",
};

const COLUMNAS = [
  { campo: "puede_crear", etiqueta: "Crear" },
  { campo: "puede_leer", etiqueta: "Leer" },
  { campo: "puede_actualizar", etiqueta: "Actualizar" },
  { campo: "puede_eliminar", etiqueta: "Eliminar" },
  { campo: "puede_ejecutar_batch", etiqueta: "Ejecutar Batch" },
];

export default function AdministracionPermisos() {
  const [matriz, setMatriz] = useState([]);
  const [recursos, setRecursos] = useState([]);
  const [cambiosPendientes, setCambiosPendientes] = useState({});
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);
  const [guardando, setGuardando] = useState(false);

  useEffect(() => {
    cargar();
  }, []);

  async function cargar() {
    const { data, error } = await obtenerMatrizPermisos();
    if (error) {
      setError(error);
      return;
    }
    setMatriz(data.matriz);
    setRecursos(data.recursos);
    setCambiosPendientes({});
  }

  function marcar(rol, recurso, campo, valorActual) {
    const clave = `${rol}__${recurso}`;
    setCambiosPendientes((previo) => ({
      ...previo,
      [clave]: {
        ...(previo[clave] || { rol, recurso }),
        [campo]: !valorActual,
      },
    }));

    setMatriz((previo) =>
      previo.map((fila) => {
        if (fila.rol !== rol) return fila;
        return {
          ...fila,
          permisos: fila.permisos.map((p) =>
            p.recurso === recurso ? { ...p, [campo]: !valorActual } : p
          ),
        };
      })
    );
  }

  async function guardar() {
    setMensaje(null);
    setError(null);
    setGuardando(true);

    const cambios = Object.values(cambiosPendientes);
    const { data, error } = await actualizarMatrizPermisos(cambios);

    setGuardando(false);

    if (error) {
      setError(error);
      return;
    }

    setMensaje(data.mensaje);
    setCambiosPendientes({});
  }

  return (
    <div className="contenedor">
      <h2>Matriz de control de permisos</h2>
      <p>
        Define, por rol y por módulo.
      </p>

      {mensaje && <p style={{ color: "#8fd18f" }}>{mensaje}</p>}
      {error && <p style={{ color: "#ff6b6b" }}>{error}</p>}

      {recursos.map((recurso) => (
        <div key={recurso} style={{ marginBottom: 28 }}>
          <h3>{ETIQUETAS_RECURSO[recurso] || recurso}</h3>
          <table>
            <thead>
              <tr>
                <th>Rol</th>
                {COLUMNAS.map((col) => (
                  <th key={col.campo}>{col.etiqueta}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {matriz.map((fila) => {
                const permiso = fila.permisos.find((p) => p.recurso === recurso);
                if (!permiso) return null;
                return (
                  <tr key={`${fila.rol}-${recurso}`}>
                    <td>{fila.rol}</td>
                    {COLUMNAS.map((col) => (
                      <td key={col.campo} style={{ textAlign: "center" }}>
                        <input
                          type="checkbox"
                          checked={permiso[col.campo]}
                          onChange={() => marcar(fila.rol, recurso, col.campo, permiso[col.campo])}
                        />
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ))}

      <button onClick={guardar} disabled={guardando || Object.keys(cambiosPendientes).length === 0}>
        {guardando ? "Guardando..." : "Guardar cambios"}
      </button>
    </div>
  );
}
