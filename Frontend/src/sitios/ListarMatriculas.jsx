import { useState, useEffect } from "react";
import {
  listarMatriculas,
  listarEstadosMatricula,
  validarRequisitos,
  registrarPago,
  generarFichaOficial,
} from "../servicios/matricula.servicio";

export default function ListarMatriculas() {
  const [matriculas, setMatriculas] = useState([]);
  const [estados, setEstados] = useState([]);
  const [mensaje, setMensaje] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarDatos();
  }, []);

  async function cargarDatos() {
    const [resMatriculas, resEstados] = await Promise.all([
      listarMatriculas(),
      listarEstadosMatricula(),
    ]);

    if (!resMatriculas.error) setMatriculas(resMatriculas.data);
    if (!resEstados.error) setEstados(resEstados.data);
  }

  function nombreEstado(estadoId) {
    const estado = estados.find((e) => e.id === estadoId);
    return estado ? estado.nombre : estadoId;
  }

  async function manejarValidar(id) {
    setMensaje(null);
    setError(null);
    const { data, error } = await validarRequisitos(id);
    if (error) return setError(error);
    setMensaje(data.mensaje);
    cargarDatos();
  }

  async function manejarPago(id) {
    setMensaje(null);
    setError(null);
    const { data, error } = await registrarPago(id);
    if (error) return setError(error);
    setMensaje(data.mensaje);
    cargarDatos();
  }

  async function manejarFicha(id) {
    setMensaje(null);
    setError(null);
    const { data, error } = await generarFichaOficial(id);
    if (error) return setError(error);
    setMensaje(data.mensaje);
    cargarDatos();
  }

  return (
    <div>
      <h2>Matrículas</h2>
      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      <table border="1" cellPadding="5">
        <thead>
          <tr>
            <th>ID</th>
            <th>Estudiante ID</th>
            <th>Estado</th>
            <th>Pagado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {matriculas.map((m) => (
            <tr key={m.id}>
              <td>{m.id}</td>
              <td>{m.estudiante_id}</td>
              <td>{nombreEstado(m.estado_id)}</td>
              <td>{m.pagado ? "Sí" : "No"}</td>
              <td>
                <button onClick={() => manejarValidar(m.id)}>Validar</button>
                <button onClick={() => manejarPago(m.id)}>Registrar pago</button>
                <button onClick={() => manejarFicha(m.id)}>Generar ficha oficial</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}