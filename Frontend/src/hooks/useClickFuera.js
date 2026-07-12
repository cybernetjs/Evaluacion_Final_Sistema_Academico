import { useEffect } from "react";

export default function useClickFuera(referencia, callback) {
  useEffect(() => {
    function manejarClick(evento) {
      if (referencia.current && !referencia.current.contains(evento.target)) {
        callback();
      }
    }

    document.addEventListener("mousedown", manejarClick);
    return () => document.removeEventListener("mousedown", manejarClick);
  }, [referencia, callback]);
}
