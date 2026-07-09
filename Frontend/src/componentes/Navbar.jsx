import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const ENLACES_POR_ROL = {
  estudiante: [
    { to: "/matricula/solicitar", texto: "Matricula" },
    { to: "/notas/mi-hoja", texto: "Mis notas" },
    { to: "/record-academico/mi-historial", texto: "Mi historial" },
    { to: "/certificados/solicitar", texto: "Certificados" },
  ],
  docente: [
    { to: "/cursos-docentes/mis-cursos", texto: "Mis cursos" },
    { to: "/notas/registrar", texto: "Registrar notas" },
  ],
  administrador: [
    { to: "/matricula/listar", texto: "Matriculas" },
    { to: "/cursos-docentes/asignar", texto: "Cursos y docentes" },
    { to: "/notas/gestionar", texto: "Actas y notas" },
    { to: "/certificados/listar", texto: "Certificados" },
    { to: "/administracion/usuarios", texto: "Usuarios y roles" },
  ],
  direccion: [
    { to: "/matricula/estadisticas", texto: "Estadisticas" },
    { to: "/cursos-docentes/carga-docente", texto: "Carga docente" },
    { to: "/notas/gestionar", texto: "Indicadores" },
    { to: "/record-academico/reportes", texto: "Record academico" },
    { to: "/administracion/auditorias", texto: "Auditorias" },
  ],
};

export default function Navbar() {
  const { usuario, cerrarSesion, estaAutenticado } = useAuth();
  const navigate = useNavigate();
  const enlaces = estaAutenticado ? ENLACES_POR_ROL[usuario.rol] || [] : [];

  function manejarCerrarSesion() {
    cerrarSesion();
    navigate("/login");
  }

  return (
    <nav>
      <Link className="marca" to="/">Sistema Academico</Link>
      <div className="nav-enlaces">
        <Link to="/">Modulos</Link>
        {enlaces.map((enlace) => (
          <Link key={enlace.to} to={enlace.to}>
            {enlace.texto}
          </Link>
        ))}
      </div>
      {estaAutenticado ? (
        <>
          <span>{usuario.username} ({usuario.rol})</span>
          <button onClick={manejarCerrarSesion}>Cerrar sesion</button>
        </>
      ) : (
        <Link className="boton-enlace boton-nav" to="/login">Iniciar sesion</Link>
      )}
    </nav>
  );
}
