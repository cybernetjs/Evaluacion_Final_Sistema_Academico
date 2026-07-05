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
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    cargarDatos();
  }, []);

  async function cargarDatos() {
    setCargando(true);
    const [resMatriculas, resEstados] = await Promise.all([
      listarMatriculas(),
      listarEstadosMatricula(),
    ]);
    setCargando(false);

    if (!resMatriculas.error) setMatriculas(resMatriculas.data);
    if (!resEstados.error) setEstados(resEstados.data);
  }

  function nombreEstado(estadoId) {
    const estado = estados.find((e) => e.id === estadoId);
    return estado ? estado.nombre : estadoId;
  }

  function puedeValidar(matricula) {
    return matricula.estado_id === 1;
  }

  function puedeRegistrarPago(matricula) {
    return matricula.estado_id === 2 && !matricula.pagado;
  }

  function puedeGenerarFicha(matricula) {
    return matricula.pagado === true;
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
    <div className="contenedor">
      <h2>Matrículas</h2>
      <p>Revisa las solicitudes, valida requisitos, registra el pago y genera la ficha oficial.</p>
      {mensaje && <p style={{ color: "green" }}>{mensaje}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {cargando ? (
        <p>Cargando matrículas...</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Estudiante</th>
              <th>Periodo</th>
              <th>Semestre</th>
              <th>Estado</th>
              <th>Pagado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {matriculas.length > 0 ? (
              matriculas.map((m) => (
                <tr key={m.id}>
                  <td>{m.id}</td>
                  <td>{m.estudiante_id}</td>
                  <td>{m.periodo_academico_id}</td>
                  <td>{m.semestre_id}</td>
                  <td>{nombreEstado(m.estado_id)}</td>
                  <td>{m.pagado ? "Sí" : "No"}</td>
                  <td>
                    <button type="button" onClick={() => manejarValidar(m.id)} disabled={!puedeValidar(m)}>
                      Validar
                    </button>
                    <button type="button" onClick={() => manejarPago(m.id)} disabled={!puedeRegistrarPago(m)}>
                      Registrar pago
                    </button>
                    <button type="button" onClick={() => manejarFicha(m.id)} disabled={!puedeGenerarFicha(m)}>
                      Generar ficha oficial
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7">No hay matrículas registradas.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}