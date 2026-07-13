import { useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../contexto/AuthContext";
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

export default function Navbar() {
  const { usuario, cerrarSesion, estaAutenticado } = useAuth();
  const [perfilAbierto, setPerfilAbierto] = useState(false);
  const perfilRef = useRef(null);
  const navigate = useNavigate();
  const location = useLocation();

  useClickFuera(perfilRef, () => setPerfilAbierto(false));

  if (!estaAutenticado) {
    return null;
  }

  function manejarCerrarSesion() {
    cerrarSesion();
    navigate("/login");
  }

  const enlaces = ENLACES_POR_ROL[usuario.rol] || [];
  const rolFormateado = usuario.rol?.toUpperCase() || "USUARIO";
  const inicial = usuario.username?.charAt(0)?.toUpperCase() || "U";

  return (
    <>
      <header className="barra-superior">
        <Link className="marca-sistema" to="/">
          <span>
            <strong>Sistema Academico</strong>
            <small>Gestion institucional</small>
          </span>
        </Link>

        <div className="acciones-superiores">
          <div className="perfil-menu" ref={perfilRef}>
            <button
              className="perfil-trigger"
              type="button"
              onClick={() => setPerfilAbierto((abierto) => !abierto)}
            >
              <span>
                <strong>{usuario.username}</strong>
                <small>{rolFormateado}</small>
              </span>
              <span className="avatar-usuario">{inicial}</span>
            </button>

            {perfilAbierto && (
              <div className="perfil-desplegable">
                <div className="perfil-cabecera">
                  <span className="avatar-usuario grande">{inicial}</span>
                  <div>
                    <strong>{usuario.username}</strong>
                    <small>{rolFormateado}</small>
                  </div>
                </div>
                <button type="button" onClick={manejarCerrarSesion}>
                  Cerrar sesion
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <nav className="menu-lateral">
        {enlaces.map((enlace) => (
          <Link
            className={location.pathname === enlace.to ? "activo" : ""}
            key={enlace.to}
            onClick={() => setPerfilAbierto(false)}
            to={enlace.to}
          >
            <span>{enlace.texto}</span>
          </Link>
        ))}
      </nav>
    </>
  );
}
