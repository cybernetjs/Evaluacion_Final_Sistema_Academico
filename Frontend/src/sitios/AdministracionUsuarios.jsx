import { useEffect, useState } from "react";
import { cambiarRol, listarUsuarios } from "../servicios/administracion.servicio";

const ROLES = ["estudiante", "docente", "administrador", "direccion"];

export default function AdministracionUsuarios() {
  const [usuarios, setUsuarios] = useState([]);
  const [selecciones, setSelecciones] = useState({});
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarUsuarios();
  }, []);

  async function cargarUsuarios() {
    const { data, error } = await listarUsuarios();
    if (error) {
      setError(error);
      return;
    }

    setUsuarios(data);
    const inicial = {};
    data.forEach((usuario) => {
      inicial[usuario.id] = usuario.rol;
    });
    setSelecciones(inicial);
  }

  async function manejarCambio(usuarioId) {
    setMensaje(null);
    setError(null);

    const { data, error } = await cambiarRol(usuarioId, selecciones[usuarioId]);

    if (error) {
      setError(error);
      return;
    }

    setMensaje(data.mensaje);
    cargarUsuarios();
  }

  return (
    <div className="contenedor">
      <h2>Usuarios y roles</h2>
      <p>Administra el acceso del sistema por perfil de usuario.</p>

      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Usuario</th>
            <th>Rol actual</th>
            <th>Nuevo rol</th>
            <th>Acción</th>
          </tr>
        </thead>
        <tbody>
          {usuarios.map((usuario) => (
            <tr key={usuario.id}>
              <td>{usuario.id}</td>
              <td>{usuario.username}</td>
              <td>{usuario.rol}</td>
              <td>
                <select
                  value={selecciones[usuario.id] || usuario.rol}
                  onChange={(e) =>
                    setSelecciones((previo) => ({
                      ...previo,
                      [usuario.id]: e.target.value,
                    }))
                  }
                >
                  {ROLES.map((rol) => (
                    <option key={rol} value={rol}>
                      {rol}
                    </option>
                  ))}
                </select>
              </td>
              <td>
                <button onClick={() => manejarCambio(usuario.id)}>Actualizar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}