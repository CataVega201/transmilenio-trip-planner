import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [conexion, setConexion] = useState('Conectando con el servidor…')

  useEffect(() => {
    const controller = new AbortController()

    async function comprobarConexion() {
      try {
        const respuesta = await fetch('/api/estado', {
          signal: controller.signal,
        })
        if (!respuesta.ok) throw new Error('Respuesta incorrecta')
        const datos = await respuesta.json()
        if (datos.estado !== 'ok') throw new Error('Estado incorrecto')
        setConexion('Conexión con Python funcionando')
      } catch {
        if (!controller.signal.aborted) {
          setConexion('No se pudo conectar. Comprueba que el servidor de Python esté abierto y recarga la página.')
        }
      }
    }

    comprobarConexion()
    return () => controller.abort()
  }, [])

  return (
    <main id="center">
      <div>
        <h1>Planeador TransMilenio</h1>
        <p>Prueba de configuración inicial</p>
      </div>
      <p role="status">{conexion}</p>
    </main>
  )
}

export default App
