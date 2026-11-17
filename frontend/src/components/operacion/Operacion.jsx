import { useRef, useState } from 'react'
import {
  agregarParada, cerrarEstacion, consultarRecorrido, deshacer,
  quitarParada, reabrirEstacion, rehacer,
} from '../../api'
import './operacion.css'

// Pantalla de operación de la red: R7 (recorrido y edición de rutas),
// R8 (cerrar y reabrir) y R9 (deshacer y rehacer). Solo confirma un cambio
// cuando el motor responde; tras un cambio real llama a onCambio para que
// Consultas y Viajes vuelvan a pedir sus datos.

// Texto para cuando el motor responde False (no hubo cambio).
const SIN_CAMBIO = {
  agregar: 'No se agregó la parada. Revisa que la ruta exista, que la estación anterior esté en la ruta y que la nueva no esté ya en ella.',
  quitar: 'No se quitó la parada: esa estación no está en la ruta.',
  cerrar: 'No hubo cambio: la estación no existe o ya estaba cerrada.',
  reabrir: 'No hubo cambio: la estación no existe o ya estaba abierta.',
  deshacer: 'No hay acciones para deshacer.',
  rehacer: 'No hay acciones para rehacer.',
}

// Una acción a la vez; respuestas viejas no pisan a las nuevas.
function useAccion() {
  const [estado, guardar] = useState({ tipo: 'inicial' })
  const ultima = useRef(0)
  async function ejecutar(promesa, alTerminar) {
    const numero = ++ultima.current
    guardar({ tipo: 'cargando' })
    try {
      const datos = await promesa()
      if (numero !== ultima.current) return
      guardar({ tipo: 'listo', datos })
      alTerminar?.(datos)
    } catch (error) {
      if (numero !== ultima.current) return
      guardar({ tipo: 'error', mensaje: error.message })
    }
  }
  return { estado, ejecutar, ocupado: estado.tipo === 'cargando' }
}

function Mensaje({ estado, exito, sinCambio, cargando = 'Esperando respuesta del servidor…' }) {
  if (estado.tipo === 'cargando') return <p className="operacion-mensaje">{cargando}</p>
  if (estado.tipo === 'error') {
    return <p className="operacion-mensaje operacion-error"><strong>Error del servidor.</strong> {estado.mensaje}</p>
  }
  if (estado.tipo === 'listo') {
    return estado.datos
      ? <p className="operacion-mensaje operacion-exito"><strong>Hecho.</strong> {exito}</p>
      : <p className="operacion-mensaje operacion-aviso"><strong>Sin cambios.</strong> {sinCambio}</p>
  }
  return null
}

function Recorrido({ versionRed }) {
  const { estado, ejecutar, ocupado } = useAccion()
  const [consulta, guardarConsulta] = useState(null)

  function enviar(evento) {
    evento.preventDefault()
    const f = new FormData(evento.currentTarget)
    const ruta = f.get('ruta').trim()
    const alReves = f.get('al_reves') === 'on'
    if (!ruta) return
    guardarConsulta({ ruta, alReves, versionRed })
    ejecutar(() => consultarRecorrido(ruta, alReves))
  }

  const desactualizado = consulta && consulta.versionRed !== versionRed && estado.tipo === 'listo'
  const paradas = estado.tipo === 'listo' ? estado.datos : null

  return (
    <section className="operacion-bloque" aria-labelledby="operacion-recorrido">
      <h3 id="operacion-recorrido">Ver recorrido de una ruta</h3>
      <form className="operacion-form" onSubmit={enviar}>
        <label>Ruta<input name="ruta" required /></label>
        <label className="operacion-check"><input type="checkbox" name="al_reves" /> Al revés</label>
        <button disabled={ocupado}>Ver recorrido</button>
      </form>
      <div role="status" aria-live="polite">
        {estado.tipo === 'cargando' && <p className="operacion-mensaje">Consultando recorrido…</p>}
        {estado.tipo === 'error' && <p className="operacion-mensaje operacion-error"><strong>Error del servidor.</strong> {estado.mensaje}</p>}
        {paradas && (paradas.length === 0
          ? <p className="operacion-mensaje operacion-aviso">La ruta {consulta.ruta} no existe o no tiene paradas.</p>
          : <>
            <p className="operacion-mensaje">
              {consulta.ruta} {consulta.alReves ? 'al revés' : 'en su sentido'}: {paradas.length} paradas.
              {desactualizado && ' La red cambió después de esta consulta; vuelve a consultar para actualizar.'}
            </p>
            <ol className="operacion-paradas">{paradas.map((parada, i) => <li key={i}>{parada}</li>)}</ol>
          </>)}
      </div>
    </section>
  )
}

function EditarRuta({ onCambio }) {
  const agregar = useAccion()
  const quitar = useAccion()
  const [ultimo, guardarUltimo] = useState({})

  function enviarAgregar(evento) {
    evento.preventDefault()
    const f = Object.fromEntries(new FormData(evento.currentTarget))
    guardarUltimo(u => ({ ...u, agregar: f }))
    agregar.ejecutar(() => agregarParada(f.ruta.trim(), f.nueva.trim(), f.despues_de.trim()), ok => ok && onCambio?.())
  }
  function enviarQuitar(evento) {
    evento.preventDefault()
    const f = Object.fromEntries(new FormData(evento.currentTarget))
    guardarUltimo(u => ({ ...u, quitar: f }))
    quitar.ejecutar(() => quitarParada(f.ruta.trim(), f.estacion.trim()), ok => ok && onCambio?.())
  }

  return (
    <section className="operacion-bloque" aria-labelledby="operacion-editar">
      <h3 id="operacion-editar">Modificar una ruta</h3>
      <form className="operacion-form" onSubmit={enviarAgregar}>
        <label>Ruta<input name="ruta" required /></label>
        <label>Estación nueva<input name="nueva" required /></label>
        <label>Justo después de<input name="despues_de" required /></label>
        <button disabled={agregar.ocupado}>Agregar parada</button>
      </form>
      <div role="status" aria-live="polite">
        <Mensaje estado={agregar.estado}
          exito={ultimo.agregar && `${ultimo.agregar.nueva} quedó en ${ultimo.agregar.ruta} después de ${ultimo.agregar.despues_de}.`}
          sinCambio={SIN_CAMBIO.agregar} />
      </div>

      <form className="operacion-form operacion-separado" onSubmit={enviarQuitar}>
        <label>Ruta<input name="ruta" required /></label>
        <label>Estación a quitar<input name="estacion" required /></label>
        <button disabled={quitar.ocupado}>Quitar parada</button>
      </form>
      <div role="status" aria-live="polite">
        <Mensaje estado={quitar.estado}
          exito={ultimo.quitar && `${ultimo.quitar.estacion} ya no es parada de ${ultimo.quitar.ruta}.`}
          sinCambio={SIN_CAMBIO.quitar} />
      </div>
    </section>
  )
}

function Cierres({ onCambio }) {
  const accion = useAccion()
  const [ultimo, guardarUltimo] = useState(null)
  // Estaciones cerradas desde esta pantalla, para reabrirlas con un clic.
  // El viajero no las ve en el autocompletado, pero el operador sí.
  const [cerradas, guardarCerradas] = useState([])

  function aplicar(tipo, nombre) {
    const limpio = nombre.trim()
    if (!limpio) return
    guardarUltimo({ tipo, nombre: limpio })
    const llamada = tipo === 'cerrar' ? cerrarEstacion : reabrirEstacion
    accion.ejecutar(() => llamada(limpio), ok => {
      if (!ok) return
      guardarCerradas(lista => tipo === 'cerrar'
        ? [...lista.filter(n => n !== limpio), limpio]
        : lista.filter(n => n !== limpio))
      onCambio?.()
    })
  }

  function enviar(evento) {
    evento.preventDefault()
    const tipo = evento.nativeEvent.submitter?.value || 'cerrar'
    aplicar(tipo, new FormData(evento.currentTarget).get('nombre'))
  }

  return (
    <section className="operacion-bloque" aria-labelledby="operacion-cierres">
      <h3 id="operacion-cierres">Cerrar o reabrir una estación</h3>
      <form className="operacion-form" onSubmit={enviar}>
        <label>Estación<input name="nombre" required /></label>
        <button name="tipo" value="cerrar" disabled={accion.ocupado}>Cerrar</button>
        <button name="tipo" value="reabrir" disabled={accion.ocupado} className="operacion-secundario">Reabrir</button>
      </form>
      <div role="status" aria-live="polite">
        <Mensaje estado={accion.estado}
          exito={ultimo && `${ultimo.nombre} quedó ${ultimo.tipo === 'cerrar' ? 'cerrada' : 'abierta'}.`}
          sinCambio={ultimo && SIN_CAMBIO[ultimo.tipo]} />
      </div>
      {cerradas.length > 0 && (
        <div className="operacion-cerradas">
          <p>Cerradas desde esta pantalla:</p>
          <ul>
            {cerradas.map(nombre => (
              <li key={nombre}>
                <span>{nombre}</span>
                <button type="button" className="operacion-secundario" disabled={accion.ocupado}
                  onClick={() => aplicar('reabrir', nombre)}>Reabrir</button>
              </li>
            ))}
          </ul>
          <p className="operacion-nota">Esta lista solo recuerda lo hecho aquí; si recargas la página o usas deshacer, consulta el estado en la sección de consultas.</p>
        </div>
      )}
    </section>
  )
}

function Historial({ onCambio }) {
  const accion = useAccion()
  const [ultimo, guardarUltimo] = useState(null)

  function aplicar(tipo) {
    guardarUltimo(tipo)
    accion.ejecutar(tipo === 'deshacer' ? deshacer : rehacer, ok => ok && onCambio?.())
  }

  return (
    <section className="operacion-bloque" aria-labelledby="operacion-historial">
      <h3 id="operacion-historial">Historial de cambios</h3>
      <p className="operacion-nota">Deshace o rehace la última modificación de rutas o cierres.</p>
      <div className="operacion-form">
        <button type="button" disabled={accion.ocupado} onClick={() => aplicar('deshacer')}>Deshacer</button>
        <button type="button" disabled={accion.ocupado} onClick={() => aplicar('rehacer')}>Rehacer</button>
      </div>
      <div role="status" aria-live="polite">
        <Mensaje estado={accion.estado}
          exito={ultimo === 'deshacer' ? 'Se deshizo el último cambio.' : 'Se rehízo el cambio.'}
          sinCambio={ultimo && SIN_CAMBIO[ultimo]} />
      </div>
    </section>
  )
}

export default function Operacion({ versionRed = 0, onCambio }) {
  return (
    <section className="operacion-panel" aria-labelledby="operacion-titulo">
      <h2 id="operacion-titulo">Operar la red</h2>
      <p className="operacion-nota">
        Los cambios se aplican en el servidor y afectan las consultas y viajes de toda la página.
      </p>
      <div className="operacion-rejilla">
        <Recorrido versionRed={versionRed} />
        <EditarRuta onCambio={onCambio} />
        <Cierres onCambio={onCambio} />
        <Historial onCambio={onCambio} />
      </div>
    </section>
  )
}
