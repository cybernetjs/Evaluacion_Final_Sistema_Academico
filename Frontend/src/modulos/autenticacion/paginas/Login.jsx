import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { iniciarSesion as loginServicio } from "../servicios/autenticacionServicio";
import { useAuth } from "../../../nucleo/contexto/AuthContext";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(false);

  const { iniciarSesion } = useAuth();
  const navigate = useNavigate();

  async function manejarEnvio(evento) {
    evento.preventDefault();
    setError(null);
    setCargando(true);

    const { data, error } = await loginServicio(username, password);

    setCargando(false);

    if (error) {
      setError(error);
      return;
    }

    iniciarSesion(data.usuario, data.token);
    navigate("/");
  }

  return (
    <div className="pantalla-centrada">
      <div className="tarjeta-login">
        <h1>Inicio de sesion</h1>
        <form onSubmit={manejarEnvio}>
          <fieldset>
            <legend>Usuario</legend>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </fieldset>

          <fieldset>
            <legend>Contrasena</legend>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </fieldset>

          <button type="submit" disabled={cargando}>
            {cargando ? "Ingresando..." : "Ingresar"}
          </button>
        </form>
        {error && <p className="mensaje-error">{error}</p>}
      </div>
    </div>
  );
}
