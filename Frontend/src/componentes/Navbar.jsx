import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export const ENLACES_POR_ROL = {
  estudiante: [
    { to: "/", texto: "Inicio" },
    { to: "/matricula/solicitar", texto: "Solicitar matricula" },
    { to: "/notas/mi-hoja", texto: "Mis notas" },
    { to: "/record-academico/mi-historial", texto: "Mi historial" },
    { to: "/certificados/solicitar", texto: "Solicitar certificado" },
  ],
  docente: [
    { to: "/", texto: "Inicio" },
    { to: "/cursos-docentes/mis-cursos", texto: "Mis cursos" },
    { to: "/notas/registrar", texto: "Registrar notas" },
  ],
  administrador: [
    { to: "/", texto: "Inicio" },
    { to: "/matricula/listar", texto: "Matriculas" },
    { to: "/cursos-docentes/asignar", texto: "Cursos y docentes" },
    { to: "/notas/gestionar", texto: "Notas" },
    { to: "/record-academico/reportes", texto: "Reportes" },
    { to: "/certificados/listar", texto: "Certificados" },
    { to: "/administracion/usuarios", texto: "Usuarios y roles" },
    { to: "/administracion/permisos", texto: "Matriz de permisos" },
    { to: "/administracion/configuracion-ciclo", texto: "Configuración del ciclo" },
  ],
  direccion: [
    { to: "/", texto: "Inicio" },
    { to: "/matricula/estadisticas", texto: "Estadisticas matricula" },
    { to: "/cursos-docentes/carga-docente", texto: "Carga docente" },
    { to: "/cursos-docentes/auditoria-silabos", texto: "Auditoria de silabos" },
    { to: "/notas/gestionar", texto: "Notas" },
    { to: "/record-academico/reportes", texto: "Reportes" },
    { to: "/record-academico/analisis-cohorte", texto: "Analisis por cohorte" },
    { to: "/administracion/auditorias", texto: "Auditorias" },
  ],
};

export default function Navbar() {
  const { usuario, cerrarSesion, estaAutenticado } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  function manejarCerrarSesion() {
    cerrarSesion();
    navigate("/login");
  }

  if (!estaAutenticado) {
    return null;
  }

  const enlaces = ENLACES_POR_ROL[usuario.rol] || [];

  return (
    <nav>
      <div className="marca-sistema">
        <h1>Sistema</h1>
      </div>

      <div className="usuario-panel">
        <strong>{usuario.username}</strong>
      </div>

      <button type="button" onClick={manejarCerrarSesion}>
        Cerrar Sesion
      </button>

      {enlaces.map((enlace) => (
        <Link
          className={location.pathname === enlace.to ? "activo" : ""}
          key={enlace.to}
          to={enlace.to}
        >
          {enlace.texto}
        </Link>
      ))}
    </nav>
  );
}
