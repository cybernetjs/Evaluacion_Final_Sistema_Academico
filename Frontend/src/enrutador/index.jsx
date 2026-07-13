import { Navigate, Routes, Route } from "react-router-dom";
import { useAuth } from "../nucleo/contexto/AuthContext";

import rutasAutenticacion from "../modulos/autenticacion/rutas";
import rutasMatricula from "../modulos/matricula/rutas";
import rutasCursos from "../modulos/cursos/rutas";
import rutasNotas from "../modulos/notas/rutas";
import rutasRecordAcademico from "../modulos/record-academico/rutas";
import rutasCertificados from "../modulos/certificados/rutas";
import rutasAdministracion from "../modulos/administracion/rutas";

const rutasModulos = [
  ...rutasAutenticacion,
  ...rutasMatricula,
  ...rutasCursos,
  ...rutasNotas,
  ...rutasRecordAcademico,
  ...rutasCertificados,
  ...rutasAdministracion,
];

function Inicio() {
  const { estaAutenticado } = useAuth();

  if (!estaAutenticado) {
    return <Navigate to="/login" replace />;
  }

  return <main className="panel-inicio" />;
}

export default function Enrutador() {
  return (
    <Routes>
      <Route path="/" element={<Inicio />} />
      {rutasModulos.map((ruta) => (
        <Route key={ruta.path} path={ruta.path} element={ruta.element} />
      ))}
    </Routes>
  );
}
