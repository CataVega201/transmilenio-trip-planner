import { useEffect, useState } from 'react'

// Una edición de la red repite la última consulta. Una respuesta antigua
// nunca reemplaza la de la petición más reciente.
export function useConsulta(versionRed) {
  const [peticion, enviar] = useState(null)
  const [salida, guardar] = useState(null)
  useEffect(() => {
    if (!peticion) return
    let vigente = true
    Promise.resolve().then(peticion).then(
      datos => vigente && guardar({ peticion, versionRed, datos }),
      error => vigente && guardar({ peticion, versionRed, error: error.message }),
    )
    return () => { vigente = false }
  }, [peticion, versionRed])
  const actual = salida?.peticion === peticion && salida?.versionRed === versionRed
  return { consultar: fn => enviar(() => fn), salida: actual ? salida : null, cargando: !!peticion && !actual }
}
