import { useState } from 'react'
import { consultarEstado, consultarRango, consultarRanking, consultarProximoBus } from '../../api'
import Estacion from './Estacion'
import { useConsulta } from './useConsulta'
import './consultas.css'

const opciones = { estado: 'Estado de estación', bus: 'Próximo bus', rango: 'Rango alfabético', ranking: 'Estaciones con más buses' }
const estados = { ABIERTA: 'La estación está abierta.', CERRADA: 'La estación está cerrada.', NO_EXISTE: 'No se encontró la estación.' }

function Formulario({ modo, versionRed }) {
  const { consultar, salida, cargando } = useConsulta(versionRed)
  function enviar(e) {
    e.preventDefault()
    const f = Object.fromEntries(new FormData(e.currentTarget))
    const acciones = {
      estado: () => consultarEstado(f.estacion),
      bus: () => consultarProximoBus(f.estacion, f.ruta, f.hora),
      rango: () => consultarRango(f.desde, f.hasta),
      ranking: () => consultarRanking(f.k),
    }
    consultar(acciones[modo])
  }
  const datos = salida?.datos
  return <><form className="consulta-form" onSubmit={enviar}>
    {(modo === 'estado' || modo === 'bus') && <Estacion etiqueta="Estación" nombre="estacion" versionRed={versionRed} />}
    {modo === 'bus' && <><label>Ruta<input name="ruta" required /></label><label>Hora del día de servicio<input name="hora" required placeholder="08:30" pattern="[0-9]{2,}:[0-5][0-9]" title="HH:MM, por ejemplo 25:10" /></label></>}
    {modo === 'rango' && <><label>Desde<input name="desde" required /></label><label>Hasta<input name="hasta" required /></label></>}
    {modo === 'ranking' && <label>Número de estaciones<input name="k" type="number" min="1" defaultValue="5" required /></label>}
    <button>Consultar</button>
  </form><div className="consulta-resultado" role="status">
    {cargando && 'Consultando…'}{salida?.error}
    {salida && !salida.error && <>
      {modo === 'estado' && estados[datos]}
      {modo === 'bus' && (datos ? 'Próximo bus a las ' + datos : 'No hay un bus disponible para esa consulta.')}
      {Array.isArray(datos) && (datos.length ? <ol>{datos.map(item =>
        Array.isArray(item) ? <li key={item[0]}>{item[0]} · {item[1]} buses</li> : <li key={item}>{item}</li>)}</ol> : 'No hay estaciones que coincidan.')}
    </>}
  </div></>
}

export default function Consultas({ versionRed = 0 }) {
  const [modo, cambiar] = useState('estado')
  return <section className="consulta-panel"><h2>Consultar la red</h2>
    <label className="consulta-selector">Tipo de consulta<select value={modo} onChange={e => cambiar(e.target.value)}>
      {Object.entries(opciones).map(([valor, texto]) => <option key={valor} value={valor}>{texto}</option>)}
    </select></label>
    <Formulario key={modo} modo={modo} versionRed={versionRed} />
  </section>
}
