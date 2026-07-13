import RutaProtegida from "../../nucleo/componentes/comunes/RutaProtegida";
import NotasMiHoja from "./paginas/NotasMiHoja";
import NotasRegistrar from "./paginas/NotasRegistrar";
import NotasGestion from "./paginas/NotasGestion";

const rutasNotas = [
  {
    path: "/notas/mi-hoja",
    element: (
      <RutaProtegida rolesPermitidos={["estudiante"]}>
        <NotasMiHoja />
      </RutaProtegida>
    ),
  },
  {
    path: "/notas/registrar",
    element: (
      <RutaProtegida rolesPermitidos={["docente"]}>
        <NotasRegistrar />
      </RutaProtegida>
    ),
  },
  {
    path: "/notas/gestionar",
    element: (
      <RutaProtegida rolesPermitidos={["administrador", "direccion"]}>
        <NotasGestion />
      </RutaProtegida>
    ),
  },
];

export default rutasNotas;
