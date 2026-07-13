import RutaProtegida from "../../nucleo/componentes/comunes/RutaProtegida";
import AdministracionUsuarios from "./paginas/AdministracionUsuarios";
import AdministracionPermisos from "./paginas/AdministracionPermisos";
import ConfiguracionGlobal from "./paginas/ConfiguracionGlobal";
import AdministracionAuditorias from "./paginas/AdministracionAuditorias";

const rutasAdministracion = [
  {
    path: "/administracion/usuarios",
    element: (
      <RutaProtegida rolesPermitidos={["administrador"]}>
        <AdministracionUsuarios />
      </RutaProtegida>
    ),
  },
  {
    path: "/administracion/permisos",
    element: (
      <RutaProtegida rolesPermitidos={["administrador"]}>
        <AdministracionPermisos />
      </RutaProtegida>
    ),
  },
  {
    path: "/administracion/configuracion-ciclo",
    element: (
      <RutaProtegida rolesPermitidos={["administrador"]}>
        <ConfiguracionGlobal />
      </RutaProtegida>
    ),
  },
  {
    path: "/administracion/auditorias",
    element: (
      <RutaProtegida rolesPermitidos={["direccion"]}>
        <AdministracionAuditorias />
      </RutaProtegida>
    ),
  },
];

export default rutasAdministracion;
