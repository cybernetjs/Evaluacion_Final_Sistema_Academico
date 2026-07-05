import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { iniciarSesion as loginServicio } from "../servicios/auth.servicio";
import { useAuth } from "../context/AuthContext";

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
        <h1>Iniciar sesión</h1>
        <form onSubmit={manejarEnvio}>
          <div>
            <label>Usuario</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div>
            <label>Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" disabled={cargando}>
            {cargando ? "Ingresando..." : "Ingresar"}
          </button>
        </form>
        {error && <p style={{ color: "#ff6b6b" }}>{error}</p>}
      </div>
    </div>
  );
}