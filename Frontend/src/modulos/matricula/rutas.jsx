import RutaProtegida from "../../nucleo/componentes/comunes/RutaProtegida";
import SolicitarMatricula from "./paginas/SolicitarMatricula";
import ListarMatriculas from "./paginas/ListarMatriculas";
import EstadisticasMatricula from "./paginas/EstadisticasMatricula";

const rutasMatricula = [
  {
    path: "/matricula/solicitar",
    element: (
      <RutaProtegida rolesPermitidos={["estudiante"]}>
        <SolicitarMatricula />
      </RutaProtegida>
    ),
  },
  {
    path: "/matricula/listar",
    element: (
      <RutaProtegida rolesPermitidos={["administrador", "direccion"]}>
        <ListarMatriculas />
      </RutaProtegida>
    ),
  },
  {
    path: "/matricula/estadisticas",
    element: (
      <RutaProtegida rolesPermitidos={["direccion"]}>
        <EstadisticasMatricula />
      </RutaProtegida>
    ),
  },
];

export default rutasMatricula;
