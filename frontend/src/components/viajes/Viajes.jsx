import { planearViaje } from '../../api'
import Estacion from '../consultas/Estacion'
import { useConsulta } from '../consultas/useConsulta'
import './viajes.css'

export default function Viajes({ versionRed = 0 }) {
  const { consultar, cargando, salida } = useConsulta(versionRed)
  function enviar(e) {
    e.preventDefault()
    const datos = new FormData(e.currentTarget)
    consultar(() => planearViaje(datos.get('origen'), datos.get('destino')))
  }
  return <section className="viaje-panel" aria-labelledby="viajes-titulo"><h2 id="viajes-titulo">Planear un viaje</h2>
    <p className="herramienta-ayuda">Escribe de dónde sales y a dónde vas. Busca el recorrido con menos paradas, directo o con un transbordo.</p>
    <form className="viaje-form" onSubmit={enviar} aria-label="Buscar un viaje">
      <Estacion etiqueta="Origen" nombre="origen" versionRed={versionRed} />
      <Estacion etiqueta="Destino" nombre="destino" versionRed={versionRed} />
      <button disabled={cargando}>Buscar recorrido</button>
    </form>
    <div className="viaje-resultado" role="status">
      {cargando && 'Buscando recorrido…'}{salida?.error}
      {salida && !salida.error && (salida.datos === null ? 'No hay recorrido disponible.'
        : salida.datos.length === 0 ? 'Ya estás en la estación de destino.'
        : <ol>{salida.datos.map(([ruta, subida, bajada], i) =>
          <li key={i}><strong>{i ? 'Transborda a ' : 'Toma '}{ruta}</strong> en {subida}. Baja en {bajada}.</li>)}</ol>)}
    </div>
  </section>
}
