import { Routes, Route } from "react-router-dom";
import Navbar from "./componentes/Navbar.jsx";
import RutaProtegida from "./rutas/RutaProtegida.jsx";
import Login from "./sitios/Login.jsx";
import SolicitarMatricula from "./sitios/SolicitarMatricula.jsx";
import ListarMatriculas from "./sitios/ListarMatriculas.jsx";
import EstadisticasMatricula from "./sitios/EstadisticasMatricula.jsx";
import CursosMisCursos from "./sitios/CursosMisCursos.jsx";
import CursosAsignar from "./sitios/CursosAsignar.jsx";
import CursosCargaDocente from "./sitios/CursosCargaDocente.jsx";
import CursosAuditoriaSilabos from "./sitios/CursosAuditoriaSilabos.jsx";
import NotasMiHoja from "./sitios/NotasMiHoja.jsx";
import NotasRegistrar from "./sitios/NotasRegistrar.jsx";
import NotasGestion from "./sitios/NotasGestion.jsx";
import RecordMiHistorial from "./sitios/RecordMiHistorial.jsx";
import RecordReportes from "./sitios/RecordReportes.jsx";
import AnalisisCohorte from "./sitios/AnalisisCohorte.jsx";
import CertificadosSolicitar from "./sitios/CertificadosSolicitar.jsx";
import CertificadosListar from "./sitios/CertificadosListar.jsx";
import AdministracionUsuarios from "./sitios/AdministracionUsuarios.jsx";
import AdministracionPermisos from "./sitios/AdministracionPermisos.jsx";
import AdministracionAuditorias from "./sitios/AdministracionAuditorias.jsx";
import ConfiguracionGlobal from "./sitios/ConfiguracionGlobal.jsx";

function Inicio() {
  return <h1>Sistema Académico</h1>;
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
          path="/cursos-docentes/auditoria-silabos"
          element={
            <RutaProtegida rolesPermitidos={["direccion"]}>
              <CursosAuditoriaSilabos />
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
          path="/record-academico/analisis-cohorte"
          element={
            <RutaProtegida rolesPermitidos={["direccion"]}>
              <AnalisisCohorte />
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
          path="/administracion/permisos"
          element={
            <RutaProtegida rolesPermitidos={["administrador"]}>
              <AdministracionPermisos />
            </RutaProtegida>
          }
        />
        <Route
          path="/administracion/configuracion-ciclo"
          element={
            <RutaProtegida rolesPermitidos={["administrador"]}>
              <ConfiguracionGlobal />
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