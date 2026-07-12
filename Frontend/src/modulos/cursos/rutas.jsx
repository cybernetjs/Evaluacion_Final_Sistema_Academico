import RutaProtegida from "../../nucleo/componentes/comunes/RutaProtegida";
import CursosMisCursos from "./paginas/CursosMisCursos";
import CursosAsignar from "./paginas/CursosAsignar";
import CursosCargaDocente from "./paginas/CursosCargaDocente";
import CursosAuditoriaSilabos from "./paginas/CursosAuditoriaSilabos";

const rutasCursos = [
  {
    path: "/cursos-docentes/mis-cursos",
    element: (
      <RutaProtegida rolesPermitidos={["docente"]}>
        <CursosMisCursos />
      </RutaProtegida>
    ),
  },
  {
    path: "/cursos-docentes/asignar",
    element: (
      <RutaProtegida rolesPermitidos={["administrador"]}>
        <CursosAsignar />
      </RutaProtegida>
    ),
  },
  {
    path: "/cursos-docentes/carga-docente",
    element: (
      <RutaProtegida rolesPermitidos={["direccion"]}>
        <CursosCargaDocente />
      </RutaProtegida>
    ),
  },
  {
    path: "/cursos-docentes/auditoria-silabos",
    element: (
      <RutaProtegida rolesPermitidos={["direccion"]}>
        <CursosAuditoriaSilabos />
      </RutaProtegida>
    ),
  },
];

export default rutasCursos;
