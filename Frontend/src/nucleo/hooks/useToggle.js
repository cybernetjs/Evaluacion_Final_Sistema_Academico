import { useCallback, useState } from "react";

export default function useToggle(valorInicial = false) {
  const [valor, setValor] = useState(valorInicial);
  const alternar = useCallback(() => setValor((actual) => !actual), []);
  return [valor, alternar, setValor];
}
