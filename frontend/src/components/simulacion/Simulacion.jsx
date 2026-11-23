import { useRef, useState } from 'react'
import { simularFila } from '../../api'
import './simulacion.css'

// Pantalla de R10. El motor hace la simulación; aquí solo se arman las
// llegadas, se envían y se resume la respuesta sin dibujar miles de filas.

const POR_PAGINA = 50
const MAX_GENERADAS = 300000

// Convierte el texto del usuario en una lista de segundos enteros >= 0.
function leerLlegadas(texto) {
  const partes = texto.split(/[\s,;]+/).filter(Boolean)
  const llegadas = []
  for (const parte of partes) {
    if (!/^\d+$/.test(parte)) {
      throw new Error(`"${parte}" no es un segundo válido. Usa enteros desde 0, separados por comas o espacios.`)
    }
    llegadas.push(Number(parte))
  }
  return llegadas
}

// Llegadas aleatorias entre 0 y "hasta", reproducibles con la semilla.
function generarLlegadas(cantidad, hasta, semilla) {
  let estado = semilla >>> 0 || 1
  const llegadas = new Array(cantidad)
  for (let i = 0; i < cantidad; i++) {
    estado = (Math.imul(estado, 1664525) + 1013904223) >>> 0
    llegadas[i] = estado % (hasta + 1)
  }
  return llegadas
}

function entero(valor, nombre, minimo) {
  const numero = Number(valor)
  if (!Number.isInteger(numero) || numero < minimo) {
    throw new Error(`${nombre} debe ser un entero mayor o igual a ${minimo}.`)
  }
  return numero
}

// Texto corto para una duración en segundos: 75 -> "1 min 15 s".
function duracion(segundos) {
  if (segundos < 60) return `${segundos} s`
  const horas = Math.floor(segundos / 3600)
  const minutos = Math.floor((segundos % 3600) / 60)
  const resto = segundos % 60
  return [horas && `${horas} h`, minutos && `${minutos} min`, resto && `${resto} s`]
    .filter(Boolean).join(' ')
}

// Resumen en una sola pasada, para que funcione con cientos de miles.
function resumir(llegadas, salidas) {
  let suma = 0
  let maxima = 0
  let sinEspera = 0
  let buses = 0
  let ultimaSalida = null
  const vistas = new Set()
  for (let i = 0; i < salidas.length; i++) {
    const espera = salidas[i] - llegadas[i]
    suma += espera
    if (espera > maxima) maxima = espera
    if (espera === 0) sinEspera++
    if (!vistas.has(salidas[i])) { vistas.add(salidas[i]); buses++ }
    if (ultimaSalida === null || salidas[i] > ultimaSalida) ultimaSalida = salidas[i]
  }
  return {
    personas: salidas.length,
    buses,
    promedio: salidas.length ? Math.round(suma / salidas.length) : 0,
    maxima,
    sinEspera,
    ultimaSalida,
  }
}

export default function Simulacion() {
  const [modo, cambiarModo] = useState('escribir')
  const [estado, guardarEstado] = useState({ tipo: 'inicial' })
  const [pagina, cambiarPagina] = useState(0)
  const ultimaPeticion = useRef(0)

  async function enviar(evento) {
    evento.preventDefault()
    const f = Object.fromEntries(new FormData(evento.currentTarget))
    let llegadas, frecuencia, capacidad
    try {
      frecuencia = entero(f.frecuencia, 'La frecuencia', 1)
      capacidad = entero(f.capacidad, 'La capacidad', 1)
      if (modo === 'escribir') {
        llegadas = leerLlegadas(f.llegadas)
      } else {
        const cantidad = entero(f.cantidad, 'La cantidad de pasajeros', 1)
        if (cantidad > MAX_GENERADAS) {
          throw new Error(`Genera como máximo ${MAX_GENERADAS.toLocaleString('es-CO')} pasajeros.`)
        }
        llegadas = generarLlegadas(cantidad, entero(f.hasta, 'El último segundo', 0), entero(f.semilla, 'La semilla', 0))
      }
    } catch (error) {
      guardarEstado({ tipo: 'error', mensaje: error.message })
      return
    }
    if (llegadas.length === 0) {
      guardarEstado({ tipo: 'vacio' })
      return
    }

    const numero = ++ultimaPeticion.current
    guardarEstado({ tipo: 'cargando', personas: llegadas.length })
    try {
      const salidas = await simularFila(llegadas, frecuencia, capacidad)
      if (numero !== ultimaPeticion.current) return
      cambiarPagina(0)
      guardarEstado({ tipo: 'exito', llegadas, salidas, frecuencia, capacidad, resumen: resumir(llegadas, salidas) })
    } catch (error) {
      if (numero !== ultimaPeticion.current) return
      guardarEstado({ tipo: 'error', mensaje: error.message })
    }
  }

  return (
    <section className="fila-panel" aria-labelledby="fila-titulo">
      <h2 id="fila-titulo">Simular la fila de abordaje</h2>
      <p className="fila-ayuda">
        El primer bus sale en el segundo <em>frecuencia</em> y luego uno cada <em>frecuencia</em> segundos.
        En cada bus suben hasta <em>capacidad</em> personas, en orden de llegada.
      </p>

      <fieldset className="fila-modos">
        <legend>¿Cómo quieres ingresar las llegadas?</legend>
        <label><input type="radio" name="fila-modo" checked={modo === 'escribir'} onChange={() => cambiarModo('escribir')} /> Escribirlas</label>
        <label><input type="radio" name="fila-modo" checked={modo === 'generar'} onChange={() => cambiarModo('generar')} /> Generarlas al azar</label>
      </fieldset>

      <form className="fila-form" onSubmit={enviar} noValidate>
        {modo === 'escribir' ? (
          <label className="fila-ancho">Segundos de llegada
            <textarea name="llegadas" rows="3" defaultValue="30, 5, 5, 70" aria-describedby="fila-llegadas-ayuda" />
            <span id="fila-llegadas-ayuda" className="fila-nota">Separados por comas o espacios. Pueden venir desordenados.</span>
          </label>
        ) : (
          <>
            <label>Pasajeros<input name="cantidad" type="number" min="1" max={MAX_GENERADAS} defaultValue="1000" /></label>
            <label>Último segundo de llegada<input name="hasta" type="number" min="0" defaultValue="3600" /></label>
            <label>Semilla<input name="semilla" type="number" min="0" defaultValue="2026" /></label>
          </>
        )}
        <label>Frecuencia (s)<input name="frecuencia" type="number" min="1" defaultValue="60" /></label>
        <label>Capacidad por bus<input name="capacidad" type="number" min="1" defaultValue="2" /></label>
        <button disabled={estado.tipo === 'cargando'}>Simular</button>
      </form>

      <div className="fila-resultado" role="status" aria-live="polite">
        {estado.tipo === 'cargando' && `Simulando ${estado.personas.toLocaleString('es-CO')} pasajeros…`}
        {estado.tipo === 'vacio' && 'No hay pasajeros para simular. Escribe al menos un segundo de llegada.'}
        {estado.tipo === 'error' && <p className="fila-error"><strong>No se pudo simular.</strong> {estado.mensaje}</p>}
        {estado.tipo === 'exito' && <Resultado {...estado} pagina={pagina} cambiarPagina={cambiarPagina} />}
      </div>
    </section>
  )
}

function Resultado({ llegadas, salidas, frecuencia, capacidad, resumen, pagina, cambiarPagina }) {
  const paginas = Math.ceil(salidas.length / POR_PAGINA)
  const inicio = pagina * POR_PAGINA
  const fin = Math.min(inicio + POR_PAGINA, salidas.length)
  const filas = []
  for (let i = inicio; i < fin; i++) filas.push(i)

  return (
    <>
      <dl className="fila-resumen">
        <div><dt>Pasajeros</dt><dd>{resumen.personas.toLocaleString('es-CO')}</dd></div>
        <div><dt>Buses con pasajeros</dt><dd>{resumen.buses.toLocaleString('es-CO')}</dd></div>
        <div><dt>Espera promedio</dt><dd>{duracion(resumen.promedio)}</dd></div>
        <div><dt>Espera máxima</dt><dd>{duracion(resumen.maxima)}</dd></div>
        <div><dt>Abordan sin esperar</dt><dd>{resumen.sinEspera.toLocaleString('es-CO')}</dd></div>
        <div><dt>Último bus</dt><dd>segundo {resumen.ultimaSalida.toLocaleString('es-CO')}</dd></div>
      </dl>
      <p className="fila-nota">
        Buses cada {frecuencia} s con cupo de {capacidad}. La tabla sigue el orden en que escribiste las llegadas.
      </p>

      <div className="fila-tabla-contenedor" role="region" tabIndex={0} aria-label="Detalle por pasajero">
        <table className="fila-tabla">
          <caption>Mostrando pasajeros {inicio + 1} a {fin} de {salidas.length.toLocaleString('es-CO')}</caption>
          <thead><tr><th scope="col">#</th><th scope="col">Llega (s)</th><th scope="col">Sale su bus (s)</th><th scope="col">Espera</th></tr></thead>
          <tbody>
            {filas.map(i => (
              <tr key={i}>
                <td>{i + 1}</td>
                <td>{llegadas[i]}</td>
                <td>{salidas[i]}</td>
                <td>{duracion(salidas[i] - llegadas[i])}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {paginas > 1 && (
        <nav className="fila-paginas" aria-label="Páginas del detalle">
          <button type="button" onClick={() => cambiarPagina(pagina - 1)} disabled={pagina === 0}>Anterior</button>
          <span>Página {pagina + 1} de {paginas.toLocaleString('es-CO')}</span>
          <button type="button" onClick={() => cambiarPagina(pagina + 1)} disabled={pagina + 1 >= paginas}>Siguiente</button>
        </nav>
      )}
    </>
  )
}
