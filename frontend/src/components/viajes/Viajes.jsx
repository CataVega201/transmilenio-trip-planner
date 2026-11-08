import { planearViaje } from '../../api'
import Estacion from '../consultas/Estacion'
import { useConsulta } from '../consultas/useConsulta'

export default function Viajes({ versionRed = 0 }) {
  const { consultar, cargando, salida } = useConsulta(versionRed)
  function enviar(e) {
    e.preventDefault()
    const datos = new FormData(e.currentTarget)
    consultar(() => planearViaje(datos.get('origen'), datos.get('destino')))
  }
  return <section className="consulta-panel"><h2>Planear un viaje</h2>
    <form className="consulta-form" onSubmit={enviar}>
      <Estacion etiqueta="Origen" nombre="origen" versionRed={versionRed} />
      <Estacion etiqueta="Destino" nombre="destino" versionRed={versionRed} />
      <button>Buscar recorrido</button>
    </form>
    <div className="consulta-resultado" role="status">
      {cargando && 'Buscando recorrido…'}{salida?.error}
      {salida && !salida.error && (salida.datos === null ? 'No hay recorrido disponible.'
        : salida.datos.length === 0 ? 'Ya estás en la estación de destino.'
        : <ol>{salida.datos.map(([ruta, subida, bajada, paradas], i) =>
          <li key={i}><strong>{i ? 'Transborda a ' : 'Toma '}{ruta}</strong> en {subida}. Baja en {bajada} después de {paradas} {paradas === 1 ? 'parada' : 'paradas'}.</li>)}</ol>)}
    </div>
  </section>
}
