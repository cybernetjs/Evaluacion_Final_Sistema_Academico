import { useEffect, useRef } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../contexto/AuthContext";
import useToggle from "../../hooks/useToggle";
import useClickFuera from "../../hooks/useClickFuera";

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
    { to: "/administracion/configuracion-ciclo", texto: "Configuracion del ciclo" },
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

function IconoMenu() {
  return (
    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <line x1="3" y1="6" x2="21" y2="6" />
      <line x1="3" y1="12" x2="21" y2="12" />
      <line x1="3" y1="18" x2="21" y2="18" />
    </svg>
  );
}

function IconoCerrar() {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <line x1="5" y1="5" x2="19" y2="19" />
      <line x1="19" y1="5" x2="5" y2="19" />
    </svg>
  );
}

export default function Navbar() {
  const { usuario, cerrarSesion, estaAutenticado } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [abierto, alternarAbierto, setAbierto] = useToggle(false);
  const referenciaNav = useRef(null);

  useClickFuera(referenciaNav, () => setAbierto(false));

  useEffect(() => {
    document.body.classList.toggle("nav-abierto", abierto);
  }, [abierto]);

  if (!estaAutenticado) {
    return null;
  }

  function manejarCerrarSesion() {
    cerrarSesion();
    navigate("/login");
  }

  const enlaces = ENLACES_POR_ROL[usuario.rol] || [];

  return (
    <div ref={referenciaNav}>
      <button type="button" className="nav-toggle" onClick={alternarAbierto}>
        <IconoMenu />
      </button>

      <nav className={abierto ? "abierto" : ""}>
        <div className="nav-cabecera">
          <button type="button" className="nav-cerrar" onClick={() => setAbierto(false)}>
            <IconoCerrar />
          </button>

          <div className="nav-usuario">
            <span className="nav-usuario-nombre">{usuario.username}</span>
            <span className="nav-usuario-rol">{usuario.rol}</span>
          </div>
        </div>

        <div className="nav-enlaces">
          {enlaces.map((enlace) => (
            <Link
              key={enlace.to}
              to={enlace.to}
              className={location.pathname === enlace.to ? "activo" : ""}
              onClick={() => setAbierto(false)}
            >
              {enlace.texto}
            </Link>
          ))}
        </div>

        <button type="button" className="nav-salir" onClick={manejarCerrarSesion}>
          Cerrar sesion
        </button>
      </nav>
    </div>
  );
}
