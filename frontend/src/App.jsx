import { useEffect, useRef, useState } from 'react'
import Operacion from './components/operacion/Operacion'
import Consultas from './components/consultas/Consultas'
import Viajes from './components/viajes/Viajes'
import Simulacion from './components/simulacion/Simulacion'
import Rendimiento from './components/rendimiento/Rendimiento'
import './App.css'

function Icono({ tipo }) {
  const trazos = {
    persona: <><circle cx="12" cy="8" r="3" /><path d="M5 21v-2a7 7 0 0 1 14 0v2" /></>,
    buscar: <><circle cx="10.5" cy="10.5" r="6.5" /><path d="m16 16 5 5" /></>,
    ruta: <><circle cx="5" cy="5" r="2" /><circle cx="19" cy="19" r="2" /><path d="M7 5h9a4 4 0 0 1 0 8H8a4 4 0 0 0 0 8h7" /></>,
    ajustes: <><path d="M4 6h16M4 12h16M4 18h16" /><circle cx="8" cy="6" r="2" /><circle cx="16" cy="12" r="2" /><circle cx="9" cy="18" r="2" /></>,
    flecha: <path d="M5 12h14m-6-6 6 6-6 6" />,
    bus: <><rect x="5" y="3" width="14" height="16" rx="3" /><path d="M5 11h14M8 19v2m8-2v2M8 6h8M8 15h1m6 0h1" /></>,
  }
  return <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{trazos[tipo]}</svg>
}

function App() {
  const [modo, setModo] = useState('cliente')
  const [versionRed, setVersionRed] = useState(0)
  const [conexion, setConexion] = useState({ tipo: 'cargando', texto: 'Conectando con la red…' })
  const selector = useRef(null)
  const resumen = useRef(null)

  useEffect(() => {
    const controller = new AbortController()
    async function comprobarConexion() {
      try {
        const respuesta = await fetch('/api/estado', { signal: controller.signal })
        if (!respuesta.ok) throw new Error('Respuesta incorrecta')
        const datos = await respuesta.json()
        if (datos.estado !== 'ok') throw new Error('Estado incorrecto')
        setConexion({ tipo: 'lista', texto: 'Red disponible para consultar' })
      } catch {
        if (!controller.signal.aborted) setConexion({ tipo: 'error', texto: 'Sin conexión. Espera un momento y recarga la página.' })
      }
    }
    comprobarConexion()
    return () => controller.abort()
  }, [])

  useEffect(() => {
    function cerrarFuera(evento) {
      if (selector.current?.open && !selector.current.contains(evento.target)) selector.current.open = false
    }
    document.addEventListener('pointerdown', cerrarFuera)
    return () => document.removeEventListener('pointerdown', cerrarFuera)
  }, [])

  function cambiarModo(nuevo) {
    setModo(nuevo)
    selector.current.open = false
    resumen.current.focus()
  }

  const accesos = [
    { id: 'consultas', icono: 'buscar', titulo: 'Consulta la red', texto: 'Estaciones, próximos buses y horarios.', numero: '01' },
    { id: 'viajes', icono: 'ruta', titulo: 'Encuentra tu recorrido', texto: 'De tu origen a tu destino, con menos paradas.', numero: '02' },
    ...(modo === 'operador' ? [{ id: 'operacion', icono: 'ajustes', titulo: 'Gestiona la operación', texto: 'Recorridos, estaciones y cambios de la red.', numero: '03' }] : []),
  ]

  return (
    <div className="app">
      <a className="app-salto" href="#contenido">Saltar al contenido</a>
      <header className="app-cabecera">
        <a className="app-marca" href="#contenido" aria-label="Planeador TransMilenio, inicio"><span className="app-simbolo"><Icono tipo="bus" /></span><span>Planeador<span className="app-marca-detalle">TransMilenio · Bogotá</span></span></a>
        <nav className="app-nav" aria-label="Navegación principal"><a href="#consultas">Consultas</a><a href="#viajes">Viajes</a>{modo === 'operador' && <a href="#operacion">Operación</a>}</nav>
        <details className="app-perfil" ref={selector} onKeyDown={evento => { if (evento.key === 'Escape') { selector.current.open = false; resumen.current.focus() } }}>
          <summary ref={resumen}><span className="app-avatar"><Icono tipo="persona" /></span><span><span className="app-perfil-etiqueta">Tu vista</span><strong>{modo === 'cliente' ? 'Cliente' : 'Operador'}</strong></span><span className="app-chevron" aria-hidden="true">⌄</span></summary>
          <div className="app-perfil-panel">
            <p className="app-perfil-titulo">¿Cómo quieres explorar?</p>
            <div role="group" aria-label="Seleccionar vista">
              <button type="button" aria-pressed={modo === 'cliente'} onClick={() => cambiarModo('cliente')}><Icono tipo="persona" /><span><strong>Cliente</strong><small>Consulta estaciones y planea tu viaje.</small></span><span aria-hidden="true">{modo === 'cliente' ? '✓' : '→'}</span></button>
              <button type="button" aria-pressed={modo === 'operador'} onClick={() => cambiarModo('operador')}><Icono tipo="ajustes" /><span><strong>Operador</strong><small>Gestiona rutas, simula y mide la red.</small></span><span aria-hidden="true">{modo === 'operador' ? '✓' : '→'}</span></button>
            </div>
            <p className="app-perfil-nota">Demo académica sin cuentas. Los cambios del operador afectan la red compartida.</p>
          </div>
        </details>
      </header>
      <main id="contenido" className="app-contenido" tabIndex={-1}>
        <section className="app-presentacion" aria-labelledby="titulo">
          <div className="app-introduccion">
            <p className="app-antetitulo"><span aria-hidden="true" /> BOGOTÁ, ESTACIÓN A ESTACIÓN</p>
            <h1 id="titulo">Tu próximo viaje<br />empieza <span className="app-palabra">aquí.</span></h1>
            <p className="app-descripcion">Menos vueltas. Más ciudad. Encuentra tu estación, conecta dos puntos y descubre tu próximo recorrido.</p>
            <div className="app-acciones"><a className="app-cta" href="#viajes">Planea tu viaje <Icono tipo="flecha" /></a><a className="app-enlace" href="#consultas">Explora las estaciones <span aria-hidden="true">↗</span></a></div>
            <p className="app-contexto">Un proyecto para entender cómo se mueve Bogotá.<br />Datos de referencia, sin información en tiempo real.</p>
          </div>
          <div className="app-ilustracion" aria-hidden="true">
            <div className="app-mapa-cabecera"><span>CONEXIONES QUE ACERCAN</span><span>BOG / CO</span></div>
            <svg className="app-mapa" viewBox="0 0 440 330" fill="none"><path className="app-mapa-calle" d="M0 70H440M0 140H440M0 210H440M0 280H440M70 0V330M140 0V330M210 0V330M280 0V330M350 0V330" /><path className="app-mapa-verde" d="M-20 105h240q40 0 40 40v95q0 30 30 30h170" /><path className="app-mapa-roja" d="M70 270v-80q0-40 40-40h200q40 0 40-40V40" /><circle cx="70" cy="270" r="10" className="app-nodo" /><circle cx="165" cy="150" r="7" className="app-nodo" /><circle cx="260" cy="150" r="12" className="app-nodo" /><circle cx="350" cy="40" r="10" className="app-nodo" /><circle cx="260" cy="150" r="4" fill="currentColor" /></svg>
            <span className="app-rotulo app-rotulo-inicio"><span className="app-punto-origen" /> Tu origen</span><span className="app-rotulo app-rotulo-fin"><Icono tipo="buscar" /> Tu destino</span>
            <div className="app-boleto"><span className="app-boleto-icono"><Icono tipo="bus" /></span><div><strong>La ciudad, más cerca.</strong><span>Un recorrido a la vez.</span></div><span className="app-boleto-flecha">↗</span></div>
          </div>
        </section>
        <section id="herramientas" className="app-herramientas" aria-labelledby="herramientas-titulo">
          <div className="app-seccion-cabecera"><div><p className="app-antetitulo">TU PUNTO DE PARTIDA</p><h2 id="herramientas-titulo">¿A dónde quieres llegar?</h2></div><p className="app-vista-actual" role="status">Vista {modo === 'cliente' ? 'Cliente · consulta y viaja' : 'Operador · consulta y gestiona'}</p></div>
          <nav className="app-accesos" aria-label="Herramientas disponibles">{accesos.map(acceso => <a key={acceso.id} className="app-acceso" href={`#${acceso.id}`}><span className="app-acceso-icono"><Icono tipo={acceso.icono} /></span><span className="app-acceso-contenido"><span className="app-numero">{acceso.numero} / EXPLORA</span><strong>{acceso.titulo}</strong><span>{acceso.texto}</span></span><Icono tipo="flecha" /></a>)}</nav>
          <div className="app-destino" id="consultas"><Consultas versionRed={versionRed} /></div><div className="app-destino" id="viajes"><Viajes versionRed={versionRed} /></div>
        </section>
        <div id="herramientas-operador" hidden={modo !== 'operador'}>
          <div className="app-operador-cabecera"><div><p className="app-antetitulo">DETRÁS DE CADA RECORRIDO</p><h2>Tu centro de operación</h2></div><p>Administra cambios y explora cómo funciona la red. Esta demo es compartida: no requiere iniciar sesión.</p></div>
          <nav className="app-subnav" aria-label="Herramientas de operador"><a href="#operacion">Gestionar red</a><a href="#simulacion">Simular abordaje</a><a href="#rendimiento">Medir rendimiento</a></nav>
          <div className="app-destino" id="operacion"><Operacion versionRed={versionRed} onCambio={() => setVersionRed(version => version + 1)} /></div><div className="app-destino" id="simulacion"><Simulacion /></div><div className="app-destino" id="rendimiento"><Rendimiento /></div>
        </div>
      </main>
      <footer className="app-pie"><div><a className="app-pie-marca" href="#contenido">Bogotá, estación a estación. <span aria-hidden="true">↗</span></a><p>Proyecto de Estructuras de Datos y Algoritmos.<br />No es un servicio oficial de TransMilenio.</p></div><p className={`app-conexion app-conexion-${conexion.tipo}`} role="status"><span aria-hidden="true" />{conexion.texto}</p></footer>
    </div>
  )
}
export default App
