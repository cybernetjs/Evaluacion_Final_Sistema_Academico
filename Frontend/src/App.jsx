import { Routes, Route } from "react-router-dom";
import Login from "./sitios/Login.jsx";

function Inicio() {
  return <h1>Sistema Académico Hola mundo xd</h1>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Inicio />} />
      <Route path="/login" element={<Login />} />
    </Routes>
  );
}