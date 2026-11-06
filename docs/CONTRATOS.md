# Acuerdos del motor y de la conexion web

Version propuesta 1 para trabajo coordinado. El profesor entrego las firmas,
las restricciones y las necesidades; no los formatos detallados de retorno ni
todas las reglas de borde. Las respuestas y politicas que se fijan aqui son
DECISIONES DEL EQUIPO. Antes de implementar su parte, cada integrante confirma
este documento o propone un cambio en su Issue. No son una garantia de lo que
esperara el script del profesor.

## 1. Reglas oficiales que no cambiamos

Se importa `Red` y `simular_fila` desde `motor`. Se conserva el nombre y orden
de parametros del enunciado, incluidos `al_reves=False`. Toda la logica R1 a R10
vive en `motor/`. El motor solo lee los tres CSV de la carpeta recibida.

Dentro de `motor/` no se usan `dict`, `set`, `sorted`, `.sort()`, `min` o `max`
sobre colecciones, busqueda con `x in lista`, `.index()`, `.count()`, `bisect`,
`heapq`, `collections`, `functools` ni librerias externas. Los registros del
motor son clases propias o listas con campos documentados; no se esconden
diccionarios en comprensiones, literales `{}` o funciones de ayuda externas.

Los modulos de biblioteca permitidos explicitamente son `csv`, `time` y `random`.
Los imports entre nuestros propios archivos de `motor/` son necesarios y se
permiten como organizacion del paquete. No importar un modulo externo que haga
el algoritmo por nosotros. Los tests, el servidor, conversor y mediciones estan
fuera del motor y pueden usar otras herramientas.

## 2. Nombres, tiempos y carga

Decisiones del grupo:

- Las consultas de nombres y rutas se normalizan quitando espacios exteriores,
  pasando a mayusculas y reemplazando vocales acentuadas y U con dieresis por
  su letra simple. La letra ENE con virgulilla se conserva como letra propia.
  El contrato interno almacena solo los nombres ya normalizados. Se implementa
  con metodos de `str`, sin importar `unicodedata` en el motor.
- La conversion produce CSV UTF-8 sin BOM, encabezados exactos, sin indices
  extra, ordenes enteros y referencias validas. El lector acepta tambien BOM
  mediante `encoding='utf-8-sig'`. Los ordenes se comparan numericamente.
- `estaciones.csv`: `nombre`. `rutas.csv`: `ruta,orden,estacion`.
  `horarios.csv`: `ruta,estacion,hora`.
- El motor no supone filas preordenadas. Crea sus indices con algoritmos propios.
  Rechaza con `ValueError` un dato mal formado, una referencia inexistente o un
  orden repetido dentro de una ruta, indicando archivo y fila.
- Una ruta representa UN sentido. En la conversion se distinguen patrones de
  paradas incompatibles de una misma linea con identificadores de ruta distintos;
  no se mezclan solo porque coincida el nombre comercial.
- Cada estacion es unica en `estaciones.csv` y aparece como maximo una vez en
  cada ruta normalizada. Si un recorrido GTFS repite una estacion, el conversor
  debe detectarlo y reportar la politica aplicada; no borrarlo silenciosamente.
- Varias filas identicas de `horarios.csv` pueden representar buses distintos.
  Se conservan como eventos distintos para contar buses, aunque R4 devuelva
  una sola hora. La deduplicacion de estaciones no deduplica eventos.
- `HH:MM` admite horas mayores de 23; por ejemplo `25:10` son 1510 minutos
  desde el inicio del dia de servicio. Se conserva ese formato y no se transforma
  a `01:10`. Los minutos van de 00 a 59. Horas de dos digitos como minimo,
  sin segundos; se comparan por minutos, nunca por texto.
- R4 busca dentro del mismo dia de servicio y no inventa una repeticion al dia
  siguiente. Un bus exactamente a la hora consultada SI es elegible.
- Todas las estaciones empiezan abiertas. Cargar no agrega una accion a deshacer.
- Ruta inexistente, nombre inexistente y ruta vacia tienen respuestas definidas
  abajo. Parametros con tipos incompatibles producen `TypeError`; argumentos
  numericos o formatos invalidos producen `ValueError`. Los bool no cuentan
  como enteros para k, frecuencia, capacidad o minutos.

No se requiere pandas para ejecutar el motor. La conversion puede usarlo si
se acuerda y registra como dependencia separada de conversion.

## 3. Respuestas publicas del motor

En esta tabla, las listas usan datos simples para que el adaptador web pueda
convertirlas sin meter JSON o Flask dentro del motor.

| Funcion oficial | Respuesta acordada |
| --- | --- |
| `Red(carpeta)` | Objeto con la red cargada desde esa carpeta; sin leer rutas absolutas del PC del autor |
| `estado(nombre)` | `"ABIERTA"`, `"CERRADA"` o `"NO_EXISTE"` |
| `autocompletar(prefijo, k)` | Lista alfabetica de hasta k nombres abiertos; `[]` si no hay coincidencias |
| `rango(desde, hasta)` | Lista alfabetica de nombres abiertos, extremos incluidos |
| `proximo_bus(estacion, ruta, hora)` | Hora `HH:MM` o `None` si no hay un bus elegible |
| `viaje(origen, destino)` | Lista de uno o dos tramos; `None` si no hay viaje; `[]` si origen y destino son la misma estacion abierta |
| `ranking(k)` | Lista de pares `[nombre, cantidad_buses]`, hasta k estaciones abiertas |
| `agregar_parada(ruta, nueva, despues_de)` | `True` si cambia la ruta; `False` si no puede hacerse |
| `quitar_parada(ruta, estacion)` | `True` si quita una parada existente; `False` si no puede hacerse |
| `recorrido(ruta, al_reves=False)` | Lista de nombres en el orden de la ruta, o `[]` si no existe o esta vacia |
| `cerrar(nombre)` / `reabrir(nombre)` | `True` si cambia el estado; `False` si no existe o ya estaba en ese estado |
| `deshacer()` / `rehacer()` | `True` si ejecuta una accion; `False` si no hay una disponible |
| `simular_fila(llegadas, frecuencia, capacidad)` | Lista de registros `[llegada, abordaje, espera]`, uno por pasajero, en orden de entrada |

Reglas adicionales:

- k debe ser entero; k menor o igual a cero devuelve `[]`. Prefijo vacio permite
  las primeras k abiertas. En rango, desde mayor que hasta devuelve `[]`.
- R1 conserva la distincion entre cerrada y ausente porque se pide consultar
  estado. Las cerradas no aparecen como opciones seleccionables en la web ni en
  autocompletado, rango o ranking. Esta es nuestra interpretacion de R1 frente
  a la frase de R8 que las excluye de las busquedas.
- En R4, estacion ausente/cerrada, ruta ausente o estacion fuera del recorrido
  actual devuelven `None`. Un formato de hora invalido produce `ValueError`.
- Las estaciones cerradas pueden atravesarse a bordo. No permiten subir,
  bajar ni transbordar. Siguen en el recorrido fisico y cuentan al medir paradas.
- Un tramo de R5 es `[ruta, subida, bajada, numero_paradas]`. El numero de paradas
  es el de enlaces recorridos: A-B-C son dos. Se sigue el sentido de la ruta.
  Se admiten cero o un transbordo; no se prometen conexiones por horario.
- En R5 gana el menor total de paradas; en empate, menos transbordos; despues,
  el orden alfabetico de ruta del primer tramo, ruta del segundo y transbordo.
  El segundo tramo y transbordo se tratan como cadena vacia en un viaje directo.
  Origen/destino ausentes o cerrados devuelven `None`, incluso si son iguales.
- R6 cuenta filas elegibles de horarios por estacion: solo rutas que aun
  incluyan esa estacion. Empates se ordenan por nombre. Se incluyen abiertas
  con cero buses. El ranking no es la cantidad de rutas distintas.
- R7 no crea estaciones ni rutas. Agregar exige ruta existente, nueva estacion
  existente, ausencia de esa estacion en la ruta y `despues_de` presente. Se
  permite agregar despues de la ultima; quitar la unica parada deja ruta vacia.
  Editar una ruta con una estacion cerrada es valido; subir alli sigue prohibido.
- Insertar una parada no inventa horarios. Quitarla desactiva sus horarios para
  esa ruta sin borrar la fuente; restaurarla vuelve a habilitarlos si existian.
  Toda consulta y ranking comprueba pertenencia al recorrido vigente.
- `recorrido` muestra tambien cerradas para que el operador vea la red completa.
  Recorrer al reves solo muestra la lista invertida; no habilita un viaje en
  el sentido contrario. El motor no modifica la ruta al consultar.
- Cierre/reapertura/edicion exitosa genera exactamente una accion. Consultar,
  fallar, cerrar dos veces o cargar no genera acciones. Un cambio nuevo exitoso
  vacia rehacer; una operacion sin efecto no lo vacia. Deshacer y rehacer no
  generan acciones adicionales y restauran indices y ranking coherentemente.

## 4. Simulacion R10

Decisiones del grupo: `llegadas` es una lista de minutos enteros no negativos,
en orden no decreciente. Cada elemento representa una persona. Puede haber
varias llegadas al mismo minuto. Frecuencia y capacidad son enteros positivos;
una llegada negativa, desordenada o un parametro no valido se rechaza.

El primer bus sale en el minuto cero y los siguientes en multiplos de frecuencia.
Una llegada en el mismo minuto que un bus puede abordar ese bus. Se respeta FIFO;
si se llena, los demas esperan. No hay limite artificial al numero de buses.
La espera es abordaje menos llegada. Una lista vacia devuelve `[]`.

Ejemplo comprobable a mano:

```text
simular_fila([0, 0, 1, 10], 10, 2)
=> [[0, 0, 0], [0, 0, 0], [1, 10, 9], [10, 10, 0]]
```

Otro: `simular_fila([0, 0, 0], 10, 2)` devuelve
`[[0, 0, 0], [0, 0, 0], [0, 10, 10]]`. Una llegada en 1000000 no debe requerir
recorrer un millon de minutos vacios; se avanza entre eventos utiles.

## 5. Limites internos entre autores

Estas interfaces son propuestas de coordinacion que cada responsable debe
confirmar antes de publicar su modulo. No son firmas adicionales del profesor.

| Modulo y propietario | Interfaz minima prevista |
| --- | --- |
| `tabla_hash.py`, Mariana | `TablaHash()`, `guardar(clave, valor)`, `obtener(clave, defecto=None)`, `eliminar(clave)` con bool, `pares()` para iterar pares; guardar reemplaza valor de clave existente |
| `horarios.py`, Catalina | `IndiceHorarios(filas)` donde cada fila es `[ruta, estacion, hora]`; `siguiente(estacion, ruta, hora)` devuelve hora o None; `cantidad(estacion, ruta)` devuelve eventos de la pareja |
| `fila.py`, Daniel | `simular_fila(llegadas, frecuencia, capacidad)` independiente de Red |
| `estaciones.py`, Mariana | `IndiceEstaciones(nombres)`; `estado(nombre)`, `autocompletar(prefijo,k)`, `rango(desde,hasta)`, `cambiar_estado(nombre,abierta)`; nombres normalizados; consultas retornan como tabla publica |
| `ranking.py`, Mariana | `IndiceRanking(filas)` con pares `[nombre, cantidad]` de abiertas; `actualizar(filas)` sustituye la base; `ranking(k)` retorna pares. Es interfaz inicial; discutir costo de actualizacion antes de implementarla |
| `rutas.py`, Alejandro | Almacen de rutas y operaciones R7; publica un adaptador para entregar conteos vigentes al ranking y restricciones a viajes/horarios |
| `red.py`, Alejandro | Fachada publica Red; coordina modulos y reglas que dependen de varios; no vuelve a implementar los algoritmos de otros |
| `__init__.py`, Alejandro | Exporta Red desde red y simular_fila desde fila; sin cargar CSV ni arrancar app al importar |

El indice de horarios solo resuelve tiempos: Red comprueba existencia, apertura y
pertenencia actual a ruta antes de llamarlo. El indice de estaciones es la fuente
unica del estado abierto/cerrado. No mantener un segundo estado en rutas o React.
Solo Red registra una accion de cambio, no el modulo y la fachada a la vez.

Antes de integrar estaciones con historial, Mariana y Alejandro fijan como se
actualizan los indices sin barrer toda la red en cada cierre. La interfaz de
ranking anterior no obliga a reconstruir todo tras cada mutacion: es un punto
de partida que se debe mejorar con una PR de contrato si los costos lo requieren.
No se declara logrado el rendimiento hasta medir las operaciones completas.

Para no bloquear A: Catalina y Daniel prueban sus modulos importando desde sus
archivos. Mientras no exista `motor/__init__.py`, Python puede tratar `motor/`
como paquete sin ese archivo. Nadie crea un `__init__.py` competidor. Si despues
la fachada importa un modulo aun no integrado, Alejandro debe corregir esa PR
antes de unirla; no dejar `main` con imports rotos.

## 6. API web prevista

TODAS las rutas siguientes, excepto `GET /api/estado`, estan pendientes. Catalina
las implementara despues de integrar las firmas correspondientes del motor.

| Peticion | Entrada | Funcion del motor |
| --- | --- | --- |
| `GET /api/estado` | Ninguna | Salud del servidor; ya existe, no es R1 |
| `GET /api/estaciones/estado` | query `nombre` | R1 |
| `GET /api/estaciones/autocompletar` | query `prefijo`, `k` | R2 |
| `GET /api/estaciones/rango` | query `desde`, `hasta` | R3 |
| `GET /api/horarios/proximo` | query `estacion`, `ruta`, `hora` | R4 |
| `GET /api/viajes` | query `origen`, `destino` | R5 |
| `GET /api/ranking` | query `k` | R6 |
| `GET /api/rutas/recorrido` | query `ruta`, `al_reves` como `true` o `false` | Consulta R7 |
| `POST /api/rutas/agregar` | JSON `ruta`, `nueva`, `despues_de` | Cambio R7 |
| `POST /api/rutas/quitar` | JSON `ruta`, `estacion` | Cambio R7 |
| `POST /api/estaciones/cerrar` | JSON `nombre` | R8 |
| `POST /api/estaciones/reabrir` | JSON `nombre` | R8 |
| `POST /api/historial/deshacer` | JSON vacio | R9 |
| `POST /api/historial/rehacer` | JSON vacio | R9 |
| `POST /api/fila` | JSON `llegadas`, `frecuencia`, `capacidad` | R10 |
| `POST /api/rendimiento` | JSON `tamanos`, `repeticiones` | Infraestructura R11 fuera del motor |

Formato comun de las rutas futuras: respuesta HTTP 200 con
`{"ok": true, "datos": ...}`; un resultado valido sin coincidencias conserva
lista vacia, false o null segun el motor. Peticion mal formada o ValueError/TypeError
de entrada: HTTP 400 con `{"ok": false, "error": {"codigo": "ENTRADA_INVALIDA",
"mensaje": "Explicacion para el usuario"}}`. Fallo inesperado: HTTP 500, codigo
`ERROR_INTERNO`, sin enviar trazas al navegador. La ruta de salud actual conserva
`{"estado":"ok","mensaje":"..."}` como excepcion documentada.

El servidor crea UNA Red compartida para la sesion local, no una por peticion,
para conservar cierres e historial. Al reiniciar vuelve a cargar los CSV abiertos;
persistencia de ediciones no es requisito y no se promete. Los cambios de red
se serializan en el adaptador para no intercalar dos modificaciones concurrentes.

Catalina centraliza `frontend/src/api.js`: `consultarEstado(nombre)`,
`autocompletar(prefijo,k)`, `consultarRango(desde,hasta)`,
`consultarProximoBus(estacion,ruta,hora)`, `planearViaje(origen,destino)`,
`consultarRanking(k)`, `consultarRecorrido(ruta,alReves=false)`,
`agregarParada(ruta,nueva,despuesDe)`, `quitarParada(ruta,estacion)`,
`cerrarEstacion(nombre)`, `reabrirEstacion(nombre)`, `deshacer()`, `rehacer()`,
`simularFila(llegadas,frecuencia,capacidad)` y `medirRendimiento(tamanos,repeticiones)`.
Cada funcion devuelve una Promise con `datos` y lanza un Error con mensaje
legible si falla; usa URLs relativas y URLSearchParams. Daniel no duplica URLs
en sus componentes. El formato de datos de R11 se fija con Daniel antes de su
integracion, sin crear dos implementaciones competidoras del adaptador.

Los componentes previstos de Daniel exportan por defecto `Operacion`,
`Simulacion` y `Rendimiento` desde `Operacion.jsx`, `Simulacion.jsx` y
`Rendimiento.jsx` en sus respectivas carpetas. Operacion recibe `onCambio` y
lo llama tras una mutacion exitosa. Los de Catalina son `Consultas` y `Viajes`,
con propiedad `versionRed`: se refrescan al cambiarla. App mantiene ese contador
y lo incrementa con `onCambio`. No recargar toda la pagina para sincronizar
estado ni modificar el estado del motor solamente en el navegador.

## 7. Cambios de acuerdos

Para proponer uno: Issue con la funcion afectada, ejemplo actual, nuevo ejemplo,
motivo, costo y autores que deben adaptar codigo. Se registra la decision en la
Issue y Catalina actualiza este documento; despues se implementa. No es necesario
reunirse a la misma hora para discutirlo. Si el profesor aclara algo, su contrato
tiene prioridad y las adaptaciones se prueban en una rama antes de integrarse.
