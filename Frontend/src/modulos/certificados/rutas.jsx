import RutaProtegida from "../../nucleo/componentes/comunes/RutaProtegida";
import CertificadosSolicitar from "./paginas/CertificadosSolicitar";
import CertificadosListar from "./paginas/CertificadosListar";

const rutasCertificados = [
  {
    path: "/certificados/solicitar",
    element: (
      <RutaProtegida rolesPermitidos={["estudiante"]}>
        <CertificadosSolicitar />
      </RutaProtegida>
    ),
  },
  {
    path: "/certificados/listar",
    element: (
      <RutaProtegida rolesPermitidos={["administrador", "direccion"]}>
        <CertificadosListar />
      </RutaProtegida>
    ),
  },
];

export default rutasCertificados;
