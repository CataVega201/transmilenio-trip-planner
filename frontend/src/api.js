async function pedir(ruta, datos, enviar = false) {
  const opciones = enviar ? {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(datos),
  } : {}
  const url = '/api/' + ruta + (enviar ? '' : '?' + new URLSearchParams(datos))
  const respuesta = await fetch(url, opciones)
  if (!respuesta.headers.get('content-type')?.includes('application/json')) {
    throw new Error('El servidor no está disponible.')
  }
  const contenido = await respuesta.json()
  if (!respuesta.ok || !contenido.ok) throw new Error(contenido.error?.mensaje || 'Error al consultar.')
  return contenido.datos
}
export const consultarEstado = (nombre) => pedir('estaciones/estado', {nombre})
export const autocompletar = (prefijo,k) => pedir('estaciones/autocompletar', {prefijo,k})
export const consultarRango = (desde,hasta) => pedir('estaciones/rango', {desde,hasta})
export const consultarProximoBus = (estacion,ruta,hora) => pedir('horarios/proximo', {estacion,ruta,hora})
export const planearViaje = (origen,destino) => pedir('viajes', {origen,destino})
export const consultarRanking = (k) => pedir('ranking', {k})
export const consultarRecorrido = (ruta,alReves=false) => pedir('rutas/recorrido', {ruta,al_reves:alReves})
export const agregarParada = (ruta,nueva,despuesDe) => pedir('rutas/agregar', {ruta,nueva,despues_de:despuesDe}, true)
export const quitarParada = (ruta,estacion) => pedir('rutas/quitar', {ruta,estacion}, true)
export const cerrarEstacion = (nombre) => pedir('estaciones/cerrar', {nombre}, true)
export const reabrirEstacion = (nombre) => pedir('estaciones/reabrir', {nombre}, true)
export const deshacer = () => pedir('historial/deshacer', {}, true)
export const rehacer = () => pedir('historial/rehacer', {}, true)
export const simularFila = (llegadas,frecuencia,capacidad) => pedir('fila', {llegadas,frecuencia,capacidad}, true)
export const medirRendimiento = (tamanos,repeticiones) => pedir('rendimiento', {tamanos,repeticiones}, true)
