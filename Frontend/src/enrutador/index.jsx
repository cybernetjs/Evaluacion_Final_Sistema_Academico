import { Navigate, Routes, Route } from "react-router-dom";
import { useAuth } from "../nucleo/contexto/AuthContext";
import { ENLACES_POR_ROL } from "../nucleo/componentes/comunes/Navbar";

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
  const { usuario, estaAutenticado } = useAuth();

  if (!estaAutenticado) {
    return <Navigate to="/login" replace />;
  }

  const modulos = (ENLACES_POR_ROL[usuario.rol] || []).filter((enlace) => enlace.to !== "/");

  return (
    <main className="panel-inicio">
      <h2>Modulos disponibles</h2>
      <div className="modulos-grid">
        {modulos.map((modulo) => (
          <a className="modulo-card" href={modulo.to} key={modulo.to}>
            {modulo.texto}
          </a>
        ))}
      </div>
    </main>
  );
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
