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
    <div className="app">
      <a className="app-salto" href="#contenido">Saltar al contenido</a>
      <header className="app-cabecera">
        <a className="app-marca" href="#contenido" aria-label="Planeador TransMilenio, inicio">
          <span className="app-simbolo" aria-hidden="true">↗</span>
          <span>Planeador<span className="app-marca-detalle">TransMilenio · Bogotá</span></span>
        </a>
        <span className="app-etiqueta">Proyecto académico</span>
      </header>

      <main id="contenido" className="app-contenido" tabIndex={-1}>
        <section className="app-presentacion" aria-labelledby="titulo">
          <div className="app-introduccion">
            <p className="app-antetitulo">BOGOTÁ, ESTACIÓN A ESTACIÓN</p>
            <h1 id="titulo">Tu próximo viaje<br />empieza aquí<span className="app-punto">.</span></h1>
            <p className="app-descripcion">Un lugar para consultar estaciones, encontrar rutas y conocer los horarios de TransMilenio.</p>
            <a className="app-enlace" href="#herramientas">Conoce las herramientas <span aria-hidden="true">↓</span></a>
          </div>
          <div className="app-ilustracion" aria-hidden="true">
            <div className="app-linea app-linea-secundaria" />
            <div className="app-linea app-linea-principal" />
            <span className="app-parada app-parada-inicio" />
            <span className="app-parada app-parada-cambio" />
            <span className="app-parada app-parada-fin" />
            <span className="app-rotulo app-rotulo-inicio">Tu origen</span>
            <span className="app-rotulo app-rotulo-fin">Tu destino</span>
            <span className="app-nota-ilustracion">Cada recorrido empieza con una estación.</span>
          </div>
        </section>

        <section id="herramientas" className="app-herramientas" aria-labelledby="herramientas-titulo">
          <div className="app-seccion-cabecera">
            <div><p className="app-antetitulo">EL PROYECTO</p><h2 id="herramientas-titulo">Todo tu recorrido, en un lugar</h2></div>
            <p className="app-aviso">Estamos construyendo estas herramientas.<br />Todavía no están disponibles para consultas.</p>
          </div>
          <div className="app-tarjetas">
            <article className="app-tarjeta"><span className="app-numero">01 / CONSULTA</span><h3>Encuentra tu estación</h3><p>Búsqueda por nombre, sugerencias y horarios del próximo bus.</p><span className="app-pendiente">En preparación</span></article>
            <article className="app-tarjeta"><span className="app-numero">02 / VIAJA</span><h3>Conecta dos puntos</h3><p>Recorridos directos o con un transbordo, priorizando menos paradas.</p><span className="app-pendiente">En preparación</span></article>
            <article className="app-tarjeta"><span className="app-numero">03 / EXPLORA</span><h3>Conoce la red</h3><p>Operación de rutas, simulación de abordaje y análisis de rendimiento.</p><span className="app-pendiente">En preparación</span></article>
          </div>
        </section>
      </main>

      <footer className="app-pie">
        <p>Proyecto de Estructuras de Datos y Algoritmos.<br />No es un servicio oficial ni ofrece información en tiempo real.</p>
        <p className="app-conexion" role="status">{conexion}</p>
      </footer>
    </div>
  )
}

export default App
