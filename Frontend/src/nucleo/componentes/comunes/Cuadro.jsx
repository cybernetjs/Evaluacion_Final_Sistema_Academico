export default function Cuadro({ titulo, children }) {
  return (
    <div className="caja">
      <span className="caja-titulo">{titulo}</span>
      <div className="caja-contenido">{children}</div>
    </div>
  );
}
