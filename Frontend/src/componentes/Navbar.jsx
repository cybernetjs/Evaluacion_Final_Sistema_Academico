import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const ENLACES_POR_ROL = {
  estudiante: [
    { to: "/matricula/solicitar", texto: "Solicitar matrícula" },
    { to: "/notas/mi-hoja", texto: "Mis notas" },
    { to: "/record-academico/mi-historial", texto: "Mi historial" },
    { to: "/certificados/solicitar", texto: "Solicitar certificado" },
  ],
  docente: [
    { to: "/cursos-docentes/mis-cursos", texto: "Mis cursos" },
    { to: "/notas/registrar", texto: "Registrar notas" },
  ],
  administrador: [
    { to: "/matricula/listar", texto: "Matrículas" },
    { to: "/cursos-docentes/asignar", texto: "Cursos y docentes" },
    { to: "/notas/gestionar", texto: "Notas" },
    { to: "/record-academico/reportes", texto: "Reportes" },
    { to: "/certificados/listar", texto: "Certificados" },
    { to: "/administracion/usuarios", texto: "Usuarios y roles" },
    { to: "/administracion/configuracion-ciclo", texto: "Configuración del ciclo" },
  ],
  direccion: [
    { to: "/matricula/estadisticas", texto: "Estadísticas matrícula" },
    { to: "/cursos-docentes/carga-docente", texto: "Carga docente" },
    { to: "/cursos-docentes/auditoria-silabos", texto: "Auditoría de sílabos" },
    { to: "/notas/gestionar", texto: "Notas" },
    { to: "/record-academico/reportes", texto: "Reportes" },
    { to: "/record-academico/analisis-cohorte", texto: "Análisis por cohorte" },
    { to: "/administracion/auditorias", texto: "Auditorías" },
  ],
};

export default function Navbar() {
  const { usuario, cerrarSesion, estaAutenticado } = useAuth();
  const navigate = useNavigate();

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
      <Link to="/">Inicio</Link>
      {enlaces.map((enlace) => (
        <Link key={enlace.to} to={enlace.to}>
          {enlace.texto}
        </Link>
      ))}
      <span>{usuario.username} ({usuario.rol})</span>
      <button onClick={manejarCerrarSesion}>Cerrar sesión</button>
    </nav>
  );
}