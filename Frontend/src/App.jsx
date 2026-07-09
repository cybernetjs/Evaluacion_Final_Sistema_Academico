import { Link, Routes, Route } from "react-router-dom";
import Navbar from "./componentes/Navbar.jsx";
import RutaProtegida from "./rutas/RutaProtegida.jsx";
import { useAuth } from "./context/AuthContext.jsx";
import Login from "./sitios/Login.jsx";
import SolicitarMatricula from "./sitios/SolicitarMatricula.jsx";
import ListarMatriculas from "./sitios/ListarMatriculas.jsx";
import EstadisticasMatricula from "./sitios/EstadisticasMatricula.jsx";
import CursosMisCursos from "./sitios/CursosMisCursos.jsx";
import CursosAsignar from "./sitios/CursosAsignar.jsx";
import CursosCargaDocente from "./sitios/CursosCargaDocente.jsx";
import NotasMiHoja from "./sitios/NotasMiHoja.jsx";
import NotasRegistrar from "./sitios/NotasRegistrar.jsx";
import NotasGestion from "./sitios/NotasGestion.jsx";
import RecordMiHistorial from "./sitios/RecordMiHistorial.jsx";
import RecordReportes from "./sitios/RecordReportes.jsx";
import CertificadosSolicitar from "./sitios/CertificadosSolicitar.jsx";
import CertificadosListar from "./sitios/CertificadosListar.jsx";
import AdministracionUsuarios from "./sitios/AdministracionUsuarios.jsx";
import AdministracionAuditorias from "./sitios/AdministracionAuditorias.jsx";

const MODULOS = [
  {
    nombre: "Matricula",
    descripcion: "Solicitudes, validacion de requisitos, pagos, fichas y estadisticas.",
    acciones: [
      { rol: "estudiante", texto: "Solicitar matricula", to: "/matricula/solicitar" },
      { rol: "administrador", texto: "Validar matriculas", to: "/matricula/listar" },
      { rol: "direccion", texto: "Supervisar estadisticas", to: "/matricula/estadisticas" },
    ],
  },
  {
    nombre: "Cursos y Docentes",
    descripcion: "Cursos asignados, silabos, asignacion docente, horarios y carga docente.",
    acciones: [
      { rol: "docente", texto: "Ver mis cursos", to: "/cursos-docentes/mis-cursos" },
      { rol: "administrador", texto: "Asignar docentes y horarios", to: "/cursos-docentes/asignar" },
      { rol: "direccion", texto: "Evaluar carga docente", to: "/cursos-docentes/carga-docente" },
    ],
  },
  {
    nombre: "Notas",
    descripcion: "Registro de notas, hoja por ciclo, actas, consolidacion e indicadores.",
    acciones: [
      { rol: "docente", texto: "Registrar notas", to: "/notas/registrar" },
      { rol: "estudiante", texto: "Consultar hoja de notas", to: "/notas/mi-hoja" },
      { rol: "administrador", texto: "Validar actas", to: "/notas/gestionar" },
      { rol: "direccion", texto: "Supervisar indicadores", to: "/notas/gestionar" },
    ],
  },
  {
    nombre: "Record Academico",
    descripcion: "Historial academico, progreso, reportes consolidados y desempeno por cohorte.",
    acciones: [
      { rol: "estudiante", texto: "Ver mi historial", to: "/record-academico/mi-historial" },
      { rol: "administrador", texto: "Generar reportes", to: "/record-academico/reportes" },
      { rol: "direccion", texto: "Analizar desempeno", to: "/record-academico/reportes" },
    ],
  },
  {
    nombre: "Certificados y Documentos",
    descripcion: "Solicitudes, autorizacion, emision y verificacion con QR.",
    acciones: [
      { rol: "estudiante", texto: "Solicitar certificado", to: "/certificados/solicitar" },
      { rol: "administrador", texto: "Emitir certificados", to: "/certificados/listar" },
      { rol: "direccion", texto: "Autorizar documentos", to: "/certificados/listar" },
    ],
  },
  {
    nombre: "Administracion y Seguridad",
    descripcion: "Usuarios, roles, auditorias, permisos y reportes estrategicos.",
    acciones: [
      { rol: "administrador", texto: "Gestionar usuarios y roles", to: "/administracion/usuarios" },
      { rol: "direccion", texto: "Revisar auditorias", to: "/administracion/auditorias" },
    ],
  },
];

function Inicio() {
  const { usuario, estaAutenticado } = useAuth();
  const rol = usuario?.rol;

  return (
    <main className="contenedor contenedor-amplio">
      <section className="encabezado-panel">
        <div>
          <p className="etiqueta">Sistema academico integral</p>
          <h1>Panel de modulos</h1>
          <p>
            Cada modulo esta organizado por responsabilidad y por rol. Ingresa con un usuario
            de prueba para ver solo las acciones permitidas.
          </p>
        </div>
        {!estaAutenticado ? (
          <Link className="boton-enlace" to="/login">Iniciar sesion</Link>
        ) : (
          <div className="resumen-usuario">
            <span>{usuario.username}</span>
            <strong>{usuario.rol}</strong>
          </div>
        )}
      </section>

      <section className="grid-modulos">
        {MODULOS.map((modulo) => {
          const accionesDisponibles = estaAutenticado
            ? modulo.acciones.filter((accion) => accion.rol === rol)
            : modulo.acciones;

          return (
            <article className="tarjeta-modulo" key={modulo.nombre}>
              <h2>{modulo.nombre}</h2>
              <p>{modulo.descripcion}</p>
              <div className="acciones-modulo">
                {accionesDisponibles.length ? (
                  accionesDisponibles.map((accion) => (
                    <Link key={`${modulo.nombre}-${accion.to}`} to={accion.to}>
                      {accion.texto}
                    </Link>
                  ))
                ) : (
                  <span>Sin acciones para este rol</span>
                )}
              </div>
            </article>
          );
        })}
      </section>
    </main>
  );
}

export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Inicio />} />
        <Route path="/login" element={<Login />} />

        <Route
          path="/matricula/solicitar"
          element={
            <RutaProtegida rolesPermitidos={["estudiante"]}>
              <SolicitarMatricula />
            </RutaProtegida>
          }
        />
        <Route
          path="/matricula/listar"
          element={
            <RutaProtegida rolesPermitidos={["administrador", "direccion"]}>
              <ListarMatriculas />
            </RutaProtegida>
          }
        />
        <Route
          path="/matricula/estadisticas"
          element={
            <RutaProtegida rolesPermitidos={["direccion"]}>
              <EstadisticasMatricula />
            </RutaProtegida>
          }
        />


        <Route
          path="/cursos-docentes/mis-cursos"
          element={
            <RutaProtegida rolesPermitidos={["docente"]}>
              <CursosMisCursos />
            </RutaProtegida>
          }
        />
        <Route
          path="/cursos-docentes/asignar"
          element={
            <RutaProtegida rolesPermitidos={["administrador"]}>
              <CursosAsignar />
            </RutaProtegida>
          }
        />
        <Route
          path="/cursos-docentes/carga-docente"
          element={
            <RutaProtegida rolesPermitidos={["direccion"]}>
              <CursosCargaDocente />
            </RutaProtegida>
          }
        />

   
        <Route
          path="/notas/mi-hoja"
          element={
            <RutaProtegida rolesPermitidos={["estudiante"]}>
              <NotasMiHoja />
            </RutaProtegida>
          }
        />
        <Route
          path="/notas/registrar"
          element={
            <RutaProtegida rolesPermitidos={["docente"]}>
              <NotasRegistrar />
            </RutaProtegida>
          }
        />
        <Route
          path="/notas/gestionar"
          element={
            <RutaProtegida rolesPermitidos={["administrador", "direccion"]}>
              <NotasGestion />
            </RutaProtegida>
          }
        />

     
        <Route
          path="/record-academico/mi-historial"
          element={
            <RutaProtegida rolesPermitidos={["estudiante"]}>
              <RecordMiHistorial />
            </RutaProtegida>
          }
        />
        <Route
          path="/record-academico/reportes"
          element={
            <RutaProtegida rolesPermitidos={["administrador", "direccion"]}>
              <RecordReportes />
            </RutaProtegida>
          }
        />

      
        <Route
          path="/certificados/solicitar"
          element={
            <RutaProtegida rolesPermitidos={["estudiante"]}>
              <CertificadosSolicitar />
            </RutaProtegida>
          }
        />
        <Route
          path="/certificados/listar"
          element={
            <RutaProtegida rolesPermitidos={["administrador", "direccion"]}>
              <CertificadosListar />
            </RutaProtegida>
          }
        />

      
        <Route
          path="/administracion/usuarios"
          element={
            <RutaProtegida rolesPermitidos={["administrador"]}>
              <AdministracionUsuarios />
            </RutaProtegida>
          }
        />
        <Route
          path="/administracion/auditorias"
          element={
            <RutaProtegida rolesPermitidos={["direccion"]}>
              <AdministracionAuditorias />
            </RutaProtegida>
          }
        />
      </Routes>
    </>
  );
}
