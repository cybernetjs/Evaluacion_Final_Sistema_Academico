import RutaProtegida from "../../nucleo/componentes/comunes/RutaProtegida";
import RecordMiHistorial from "./paginas/RecordMiHistorial";
import RecordReportes from "./paginas/RecordReportes";
import AnalisisCohorte from "./paginas/AnalisisCohorte";

const rutasRecordAcademico = [
  {
    path: "/record-academico/mi-historial",
    element: (
      <RutaProtegida rolesPermitidos={["estudiante"]}>
        <RecordMiHistorial />
      </RutaProtegida>
    ),
  },
  {
    path: "/record-academico/reportes",
    element: (
      <RutaProtegida rolesPermitidos={["administrador", "direccion"]}>
        <RecordReportes />
      </RutaProtegida>
    ),
  },
  {
    path: "/record-academico/analisis-cohorte",
    element: (
      <RutaProtegida rolesPermitidos={["direccion"]}>
        <AnalisisCohorte />
      </RutaProtegida>
    ),
  },
];

export default rutasRecordAcademico;
