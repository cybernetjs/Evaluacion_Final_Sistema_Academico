import { useEffect, useState } from "react";
import { cambiarRol, listarUsuarios, listarEspecialidades, registrarDocente, registrarPersonal } from "../servicios/administracion.servicio";
import { registrarEstudiante } from "../servicios/auth.servicio";

const ROLES = ["estudiante", "docente", "administrador", "direccion"];

const VACIO_ESTUDIANTE = {
  username: "",
  password: "",
  nombres: "",
  apellido_paterno: "",
  apellido_materno: "",
  correo_institucional: "",
  especialidad_id: "",
};

const VACIO_DOCENTE = {
  username: "",
  password: "",
  nombres: "",
  apellido_paterno: "",
  apellido_materno: "",
  correo_institucional: "",
};

const VACIO_PERSONAL = {
  username: "",
  password: "",
  rol: "administrador",
};

export default function AdministracionUsuarios() {
  const [usuarios, setUsuarios] = useState([]);
  const [selecciones, setSelecciones] = useState({});
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);

  const [pestana, setPestana] = useState("estudiante");
  const [especialidades, setEspecialidades] = useState([]);

  const [formEstudiante, setFormEstudiante] = useState(VACIO_ESTUDIANTE);
  const [formDocente, setFormDocente] = useState(VACIO_DOCENTE);
  const [formPersonal, setFormPersonal] = useState(VACIO_PERSONAL);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    cargarUsuarios();
    cargarEspecialidades();
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

  async function cargarEspecialidades() {
    const { data } = await listarEspecialidades();
    if (data) setEspecialidades(data);
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

  async function manejarAltaEstudiante(evento) {
    evento.preventDefault();
    setMensaje(null);
    setError(null);
    setEnviando(true);

    const { data, error } = await registrarEstudiante({
      ...formEstudiante,
      especialidad_id: Number(formEstudiante.especialidad_id),
    });

    setEnviando(false);

    if (error) {
      setError(error);
      return;
    }

    setMensaje("Estudiante registrado correctamente");
    setFormEstudiante(VACIO_ESTUDIANTE);
    cargarUsuarios();
  }

  async function manejarAltaDocente(evento) {
    evento.preventDefault();
    setMensaje(null);
    setError(null);
    setEnviando(true);

    const { data, error } = await registrarDocente(formDocente);

    setEnviando(false);

    if (error) {
      setError(error);
      return;
    }

    setMensaje("Docente registrado correctamente");
    setFormDocente(VACIO_DOCENTE);
    cargarUsuarios();
  }

  async function manejarAltaPersonal(evento) {
    evento.preventDefault();
    setMensaje(null);
    setError(null);
    setEnviando(true);

    const { data, error } = await registrarPersonal(formPersonal);

    setEnviando(false);

    if (error) {
      setError(error);
      return;
    }

    setMensaje(`Cuenta de ${formPersonal.rol} registrada correctamente`);
    setFormPersonal(VACIO_PERSONAL);
    cargarUsuarios();
  }

  return (
    <div className="contenedor">
      <h2>Usuarios y roles</h2>

      {mensaje && <p style={{ color: "#8fd18f" }}>{mensaje}</p>}
      {error && <p style={{ color: "#ff6b6b" }}>{error}</p>}

      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <button type="button" onClick={() => setPestana("estudiante")} disabled={pestana === "estudiante"}>
          Registrar estudiante
        </button>
        <button type="button" onClick={() => setPestana("docente")} disabled={pestana === "docente"}>
          Registrar docente
        </button>
        <button type="button" onClick={() => setPestana("personal")} disabled={pestana === "personal"}>
          Registrar administrador / dirección
        </button>
      </div>

      {pestana === "estudiante" && (
        <form onSubmit={manejarAltaEstudiante} style={{ display: "grid", gap: 8, maxWidth: 420, marginBottom: 24 }}>
          <input
            placeholder="Usuario"
            value={formEstudiante.username}
            onChange={(e) => setFormEstudiante((f) => ({ ...f, username: e.target.value }))}
            required
          />
          <input
            type="password"
            placeholder="Contraseña"
            value={formEstudiante.password}
            onChange={(e) => setFormEstudiante((f) => ({ ...f, password: e.target.value }))}
            required
          />
          <input
            placeholder="Nombres"
            value={formEstudiante.nombres}
            onChange={(e) => setFormEstudiante((f) => ({ ...f, nombres: e.target.value }))}
            required
          />
          <input
            placeholder="Apellido paterno"
            value={formEstudiante.apellido_paterno}
            onChange={(e) => setFormEstudiante((f) => ({ ...f, apellido_paterno: e.target.value }))}
            required
          />
          <input
            placeholder="Apellido materno"
            value={formEstudiante.apellido_materno}
            onChange={(e) => setFormEstudiante((f) => ({ ...f, apellido_materno: e.target.value }))}
            required
          />
          <input
            type="email"
            placeholder="Correo institucional"
            value={formEstudiante.correo_institucional}
            onChange={(e) => setFormEstudiante((f) => ({ ...f, correo_institucional: e.target.value }))}
            required
          />
          <select
            value={formEstudiante.especialidad_id}
            onChange={(e) => setFormEstudiante((f) => ({ ...f, especialidad_id: e.target.value }))}
            required
          >
            <option value="">Selecciona una especialidad</option>
            {especialidades.map((esp) => (
              <option key={esp.id} value={esp.id}>
                {esp.nombre}
              </option>
            ))}
          </select>
          <button type="submit" disabled={enviando}>
            {enviando ? "Registrando..." : "Registrar estudiante"}
          </button>
        </form>
      )}

      {pestana === "docente" && (
        <form onSubmit={manejarAltaDocente} style={{ display: "grid", gap: 8, maxWidth: 420, marginBottom: 24 }}>
          <input
            placeholder="Usuario"
            value={formDocente.username}
            onChange={(e) => setFormDocente((f) => ({ ...f, username: e.target.value }))}
            required
          />
          <input
            type="password"
            placeholder="Contraseña"
            value={formDocente.password}
            onChange={(e) => setFormDocente((f) => ({ ...f, password: e.target.value }))}
            required
          />
          <input
            placeholder="Nombres"
            value={formDocente.nombres}
            onChange={(e) => setFormDocente((f) => ({ ...f, nombres: e.target.value }))}
            required
          />
          <input
            placeholder="Apellido paterno"
            value={formDocente.apellido_paterno}
            onChange={(e) => setFormDocente((f) => ({ ...f, apellido_paterno: e.target.value }))}
            required
          />
          <input
            placeholder="Apellido materno"
            value={formDocente.apellido_materno}
            onChange={(e) => setFormDocente((f) => ({ ...f, apellido_materno: e.target.value }))}
            required
          />
          <input
            type="email"
            placeholder="Correo institucional"
            value={formDocente.correo_institucional}
            onChange={(e) => setFormDocente((f) => ({ ...f, correo_institucional: e.target.value }))}
            required
          />
          <button type="submit" disabled={enviando}>
            {enviando ? "Registrando..." : "Registrar docente"}
          </button>
        </form>
      )}

      {pestana === "personal" && (
        <form onSubmit={manejarAltaPersonal} style={{ display: "grid", gap: 8, maxWidth: 420, marginBottom: 24 }}>
          <input
            placeholder="Usuario"
            value={formPersonal.username}
            onChange={(e) => setFormPersonal((f) => ({ ...f, username: e.target.value }))}
            required
          />
          <input
            type="password"
            placeholder="Contraseña"
            value={formPersonal.password}
            onChange={(e) => setFormPersonal((f) => ({ ...f, password: e.target.value }))}
            required
          />
          <select
            value={formPersonal.rol}
            onChange={(e) => setFormPersonal((f) => ({ ...f, rol: e.target.value }))}
          >
            <option value="administrador">Administrador</option>
            <option value="direccion">Dirección</option>
          </select>
          <button type="submit" disabled={enviando}>
            {enviando ? "Registrando..." : "Registrar cuenta"}
          </button>
        </form>
      )}

      <h3>Usuarios registrados</h3>
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
