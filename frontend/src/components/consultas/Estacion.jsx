import { useEffect, useId, useState } from 'react'
import { autocompletar } from '../../api'

export default function Estacion({ etiqueta, nombre, versionRed }) {
  const id = useId()
  const [texto, cambiar] = useState('')
  const [sugerencia, guardar] = useState(null)
  useEffect(() => {
    if (!texto.trim()) return
    let vigente = true
    const reloj = setTimeout(() => {
      autocompletar(texto, 8).then(
        lista => vigente && guardar({ texto, versionRed, lista }),
        () => vigente && guardar({ texto, versionRed, lista: [] }),
      )
    }, 200)
    return () => { vigente = false; clearTimeout(reloj) }
  }, [texto, versionRed])
  const lista = sugerencia?.texto === texto && sugerencia?.versionRed === versionRed ? sugerencia.lista : []
  return <label>{etiqueta}
    <input name={nombre} required list={id} value={texto} onChange={e => cambiar(e.target.value)} autoComplete="off" />
    <datalist id={id}>{lista.map(n => <option key={n} value={n} />)}</datalist>
  </label>
}
