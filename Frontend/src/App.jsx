import { Routes, Route } from "react-router-dom";
import Navbar from "./componentes/Navbar.jsx";
import RutaProtegida from "./rutas/RutaProtegida.jsx";
import Login from "./sitios/Login.jsx";

function Inicio() {
  return <h1>Sistema Académico</h1>;
}

function PlaceholderModulo({ nombre }) {
  return <h2>Módulo: {nombre} (en construcción)</h2>;
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
              <PlaceholderModulo nombre="Solicitar matrícula" />
            </RutaProtegida>
          }
        />
        <Route
          path="/matricula/listar"
          element={
            <RutaProtegida rolesPermitidos={["administrador", "direccion"]}>
              <PlaceholderModulo nombre="Listar matrículas" />
            </RutaProtegida>
          }
        />
        <Route
          path="/matricula/estadisticas"
          element={
            <RutaProtegida rolesPermitidos={["direccion"]}>
              <PlaceholderModulo nombre="Estadísticas de matrícula" />
            </RutaProtegida>
          }
        />


        <Route
          path="/cursos-docentes/mis-cursos"
          element={
            <RutaProtegida rolesPermitidos={["docente"]}>
              <PlaceholderModulo nombre="Mis cursos" />
            </RutaProtegida>
          }
        />
        <Route
          path="/cursos-docentes/asignar"
          element={
            <RutaProtegida rolesPermitidos={["administrador"]}>
              <PlaceholderModulo nombre="Asignar docentes" />
            </RutaProtegida>
          }
        />
        <Route
          path="/cursos-docentes/carga-docente"
          element={
            <RutaProtegida rolesPermitidos={["direccion"]}>
              <PlaceholderModulo nombre="Carga docente" />
            </RutaProtegida>
          }
        />

   
        <Route
          path="/notas/mi-hoja"
          element={
            <RutaProtegida rolesPermitidos={["estudiante"]}>
              <PlaceholderModulo nombre="Mi hoja de notas" />
            </RutaProtegida>
          }
        />
        <Route
          path="/notas/registrar"
          element={
            <RutaProtegida rolesPermitidos={["docente"]}>
              <PlaceholderModulo nombre="Registrar notas" />
            </RutaProtegida>
          }
        />

     
        <Route
          path="/record-academico/mi-historial"
          element={
            <RutaProtegida rolesPermitidos={["estudiante"]}>
              <PlaceholderModulo nombre="Mi historial académico" />
            </RutaProtegida>
          }
        />
        <Route
          path="/record-academico/reportes"
          element={
            <RutaProtegida rolesPermitidos={["administrador", "direccion"]}>
              <PlaceholderModulo nombre="Reportes académicos" />
            </RutaProtegida>
          }
        />

      
        <Route
          path="/certificados/solicitar"
          element={
            <RutaProtegida rolesPermitidos={["estudiante"]}>
              <PlaceholderModulo nombre="Solicitar certificado" />
            </RutaProtegida>
          }
        />
        <Route
          path="/certificados/listar"
          element={
            <RutaProtegida rolesPermitidos={["administrador", "direccion"]}>
              <PlaceholderModulo nombre="Certificados" />
            </RutaProtegida>
          }
        />

      
        <Route
          path="/administracion/usuarios"
          element={
            <RutaProtegida rolesPermitidos={["administrador"]}>
              <PlaceholderModulo nombre="Usuarios y roles" />
            </RutaProtegida>
          }
        />
        <Route
          path="/administracion/auditorias"
          element={
            <RutaProtegida rolesPermitidos={["direccion"]}>
              <PlaceholderModulo nombre="Auditorías" />
            </RutaProtegida>
          }
        />
      </Routes>
    </>
  );
}