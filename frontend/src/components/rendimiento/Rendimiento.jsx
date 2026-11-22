import { useRef, useState } from 'react'
import { medirRendimiento } from '../../api'
import './rendimiento.css'

// Panel R11. Las mediciones las hace Python (rendimiento/medir.py) cuando se
// pide; aquí solo se eligen tamaños, se muestran los resultados y se explican.

const TAMANOS = [10000, 20000, 40000, 80000]

function tiempo(ns) {
  if (ns < 10000) return `${ns.toLocaleString('es-CO')} ns`
  if (ns < 10000000) return `${(ns / 1e3).toLocaleString('es-CO', { maximumFractionDigits: 1 })} µs`
  return `${(ns / 1e6).toLocaleString('es-CO', { maximumFractionDigits: 1 })} ms`
}

// Lectura honesta de la relación entre n y 2n, sin prometer valores exactos.
function lectura(relacion, medianaNs) {
  if (relacion == null) return ''
  if (medianaNs < 10000) return 'Tiempos de pocos microsegundos: el ruido pesa más que el tamaño.'
  if (relacion < 1.4) return 'Casi no crece al duplicar n: compatible con un costo constante o logarítmico.'
  if (relacion < 2.6) return 'Crece cerca del doble al duplicar n: compatible con un costo lineal (o n log n).'
  return 'Crece más que el doble al duplicar n: más que lineal.'
}

// Agrupa las filas por operación conservando el orden de llegada.
function agrupar(filas) {
  const grupos = []
  const indice = new Map()
  for (const fila of filas) {
    const clave = `${fila.requisito}|${fila.operacion}`
    if (!indice.has(clave)) {
      indice.set(clave, grupos.length)
      grupos.push({ clave, requisito: fila.requisito, operacion: fila.operacion,
        esperado: fila.esperado, nota: fila.nota, filas: [] })
    }
    grupos[indice.get(clave)].filas.push(fila)
  }
  return grupos
}

function Grafica({ grupo }) {
  const puntos = grupo.filas.filter(f => f.estado === 'medido')
  if (puntos.length < 2) return <p className="rendimiento-nota">Se necesitan al menos dos tamaños para dibujar la tendencia.</p>
  const ancho = 320, alto = 180, margen = 36
  const maxN = Math.max(...puntos.map(p => p.n))
  const base = puntos[0]
  const lineal = puntos.map(p => base.mediana_ns * p.n / base.n)
  const maxT = Math.max(...puntos.map(p => p.mediana_ns), ...lineal)
  const x = n => margen + (n / maxN) * (ancho - margen - 10)
  const y = t => alto - margen + 6 - (t / maxT) * (alto - margen - 10)
  const trazo = valores => valores.map((t, i) => `${i ? 'L' : 'M'}${x(puntos[i].n).toFixed(1)},${y(t).toFixed(1)}`).join(' ')
  return (
    <figure className="rendimiento-grafica">
      <svg viewBox={`0 0 ${ancho} ${alto}`} role="img"
        aria-label={`Mediana de ${grupo.operacion} según n, comparada con una referencia lineal`}>
        <line x1={margen} y1={alto - margen + 6} x2={ancho - 6} y2={alto - margen + 6} className="rendimiento-eje" />
        <line x1={margen} y1={8} x2={margen} y2={alto - margen + 6} className="rendimiento-eje" />
        <path d={trazo(lineal)} className="rendimiento-referencia" />
        <path d={trazo(puntos.map(p => p.mediana_ns))} className="rendimiento-linea" />
        {puntos.map(p => (
          <g key={p.n}>
            <circle cx={x(p.n)} cy={y(p.mediana_ns)} r="4" className="rendimiento-punto" />
            <text x={x(p.n)} y={alto - margen + 22} textAnchor="middle">{(p.n / 1000).toLocaleString('es-CO')}k</text>
          </g>
        ))}
        <text x={margen - 4} y={14} textAnchor="end">{tiempo(maxT)}</text>
        <text x={margen - 4} y={alto - margen + 6} textAnchor="end">0</text>
      </svg>
      <figcaption>
        <span><span className="rendimiento-clave rendimiento-clave-medida" /> Mediana medida</span>
        <span><span className="rendimiento-clave rendimiento-clave-referencia" /> Si creciera igual que n</span>
      </figcaption>
    </figure>
  )
}

function Operacion({ grupo }) {
  const medidas = grupo.filas.filter(f => f.estado === 'medido')
  const errores = grupo.filas.filter(f => f.estado.startsWith('error'))
  const ultima = medidas[medidas.length - 1]
  return (
    <article className="rendimiento-operacion">
      <h3><span className="rendimiento-req">{grupo.requisito}</span> {grupo.operacion}</h3>
      <div className="rendimiento-cuerpo">
        <div className="rendimiento-tabla-contenedor" tabIndex={0} aria-label={`Resultados de ${grupo.operacion}`}>
          <table className="rendimiento-tabla">
            <thead>
              <tr><th scope="col">n ({medidas[0]?.unidad})</th><th scope="col">Mediana</th><th scope="col">× anterior</th><th scope="col">Salida</th></tr>
            </thead>
            <tbody>
              {medidas.map(f => (
                <tr key={f.n}>
                  <td>{f.n.toLocaleString('es-CO')}</td>
                  <td>{tiempo(f.mediana_ns)}</td>
                  <td>{f.relacion == null ? '—' : f.relacion.toLocaleString('es-CO')}</td>
                  <td>{f.tamano_salida == null ? '—' : f.tamano_salida.toLocaleString('es-CO')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <Grafica grupo={grupo} />
        <div className="rendimiento-explicacion">
          <p><strong>Lo que espera el autor:</strong> {grupo.esperado || 'pendiente de que el autor lo confirme.'}</p>
          {ultima && <p><strong>Lectura:</strong> {lectura(ultima.relacion, ultima.mediana_ns)}</p>}
          {medidas[0]?.k != null && <p><strong>k:</strong> {medidas[0].k}</p>}
          <p className="rendimiento-nota">
            {medidas[0]?.repeticiones} repeticiones, mediana, {medidas[0]?.cache}.{grupo.nota && ` ${grupo.nota}`}
          </p>
          {errores.map(f => <p key={f.n} className="rendimiento-error">n = {f.n}: {f.estado}</p>)}
        </div>
      </div>
    </article>
  )
}

export default function Rendimiento() {
  const [elegidos, guardarElegidos] = useState(TAMANOS.slice(0, 2))
  const [estado, guardarEstado] = useState({ tipo: 'inicial' })
  const ultima = useRef(0)

  function alternar(n) {
    guardarElegidos(lista => lista.includes(n) ? lista.filter(v => v !== n) : [...lista, n].sort((a, b) => a - b))
  }

  async function medir(evento) {
    evento.preventDefault()
    const repeticiones = Number(new FormData(evento.currentTarget).get('repeticiones'))
    if (elegidos.length === 0) {
      guardarEstado({ tipo: 'error', mensaje: 'Elige al menos un tamaño.' })
      return
    }
    const numero = ++ultima.current
    guardarEstado({ tipo: 'cargando' })
    try {
      const filas = await medirRendimiento(elegidos, repeticiones)
      if (numero !== ultima.current) return
      guardarEstado({ tipo: 'listo', filas })
    } catch (error) {
      if (numero !== ultima.current) return
      guardarEstado({ tipo: 'error', mensaje: error.message })
    }
  }

  const grupos = estado.tipo === 'listo' ? agrupar(estado.filas) : []
  const medidos = grupos.filter(g => g.filas.some(f => f.estado === 'medido' || f.estado.startsWith('error')))
  const pendientes = grupos.filter(g => !medidos.includes(g))

  return (
    <section className="rendimiento-panel" aria-labelledby="rendimiento-titulo">
      <h2 id="rendimiento-titulo">Rendimiento del motor (R11)</h2>
      <p className="rendimiento-nota">
        Python mide cada operación directamente sobre el motor, sin contar el tiempo de la red HTTP.
        Se genera una red sintética por tamaño y se reporta la mediana de varias repeticiones.
      </p>

      <form className="rendimiento-form" onSubmit={medir}>
        <fieldset>
          <legend>Tamaños de la red (estaciones)</legend>
          {TAMANOS.map(n => (
            <label key={n}>
              <input type="checkbox" checked={elegidos.includes(n)} onChange={() => alternar(n)} />
              {n.toLocaleString('es-CO')}
            </label>
          ))}
        </fieldset>
        <label className="rendimiento-repeticiones">Repeticiones
          <select name="repeticiones" defaultValue="3">
            {[1, 3, 5, 7, 9].map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </label>
        <button disabled={estado.tipo === 'cargando'}>Medir</button>
      </form>
      <p className="rendimiento-nota">Con 80 000 estaciones la medición puede tardar varios minutos.</p>

      <div role="status" aria-live="polite">
        {estado.tipo === 'cargando' && <p className="rendimiento-mensaje">Midiendo en Python… no cierres la página.</p>}
        {estado.tipo === 'error' && <p className="rendimiento-mensaje rendimiento-error"><strong>No se pudo medir.</strong> {estado.mensaje}</p>}
        {estado.tipo === 'listo' && medidos.length === 0 && (
          <p className="rendimiento-mensaje">Todavía no hay operaciones disponibles para medir en este servidor.</p>
        )}
      </div>

      {medidos.map(grupo => <Operacion key={grupo.clave} grupo={grupo} />)}

      {pendientes.length > 0 && (
        <div className="rendimiento-pendientes">
          <h3>Pendientes</h3>
          <ul>
            {pendientes.map(g => <li key={g.clave}><strong>{g.requisito}</strong> {g.operacion}: {g.filas[0].estado}</li>)}
          </ul>
        </div>
      )}
    </section>
  )
}
