# Guia de Catalina Vega

Tu enfoque principal es frontend e integracion. Tambien implementas R4 y la
conversion GTFS. No tienes que construir el motor completo ni hacer commits por
tus companeros. Ya tienes aportes de configuracion registrados.

## 1. Antes de tocar codigo

Lee [la guia general](../GUIA_GENERAL.md), [Git paso a paso](../GIT_PASO_A_PASO.md)
y [los contratos](../CONTRATOS.md). Tu equipo ya esta instalado. Abre siempre en
VS Code la carpeta `transmilenio-trip-planner`, no su carpeta superior.

Las guias se prepararon en la rama `docs/guias-equipo`. Esa es una tarea de
documentacion: primero debe revisarse e integrarse siguiendo la guia de Git.
No agregues R4 o un rediseño a esa misma rama.

## 2. Archivos a tu cargo

- `motor/horarios.py` y `tests/test_horarios.py`: R4.
- `docs/decisiones/R4.md`: explicacion de R4.
- `conversion/`: script GTFS, instrucciones, pruebas y registro de la fuente.
- `frontend/src/components/consultas/` y `frontend/src/components/viajes/`.
- `frontend/src/styles/tema.css`: colores, tipografia y espacios comunes.
- Integracion de `App.jsx`, estilos globales, `api.js`, `servidor.py` y versiones
  de dependencias. Otros proponen cambios a estos archivos mediante una Issue;
  no deben editarlos al mismo tiempo.

Alejandro es el unico integrador de `motor/red.py` y `motor/__init__.py`. Tu
modulo R4 no debe importar Flask ni decidir por su cuenta si una estacion esta
abierta: Red valida eso antes de consultar el indice.

## 3. Primera tarea independiente R4

En GitHub abre la Issue `R4 - Buscar el siguiente horario`, asignatela e indica
los tres archivos de R4. Confirma la interfaz de `IndiceHorarios` del contrato.
No necesitas esperar al GTFS ni a Alejandro para empezar.

Con estado limpio, desde `main` actualizado, crea:

```cmd
git switch -c catalina/r4-horarios
```

1. Crea `motor/horarios.py`. Recibe filas `[ruta, estacion, hora]`, organiza por
   pareja y convierte las horas a minutos. No dependas del orden de entrada.
2. Considera un indice por pareja y un arreglo ordenado con algoritmo propio,
   seguido de busqueda binaria para el siguiente horario. Compara con un barrido
   lineal. Antes de reutilizar `TablaHash`, espera a que su interfaz y PR esten
   integradas; no construyas una segunda tabla compartida de forma permanente.
   Puedes empezar por probar la busqueda sobre un arreglo ya preparado.
3. Implementa `siguiente` y `cantidad`, incluidas las horas mayores de 23 y
   horarios repetidos. `cantidad` conserva todos los eventos.
4. Crea pruebas con `unittest` en `tests/test_horarios.py`. Las entradas pequenas
   se escriben en el test, fuera del motor. No hace falta un CSV para probar R4.
5. Crea `docs/decisiones/R4.md` desde la plantilla. Explica construccion, busqueda,
   cantidad de horarios de la pareja y costo total de acceso al indice.

Casos obligatorios: pareja ausente; vacio; hora exacta; antes del primer bus;
entre dos; despues del ultimo; filas desordenadas; duplicados; `23:50`, `24:05`,
`25:10`; minutos invalidos. Una salida esperada debe comprobarse con `assert`,
no solamente imprimirse.

Comando cuando el archivo exista:

```cmd
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_horarios.py" -v
```

El resultado debe tener pruebas ejecutadas y `OK`; `Ran 0 tests` no verifica R4.
Prepara solamente los tres archivos, haz un commit descriptivo, sube la rama y
abre PR. Daniel es tu revisor habitual. La integracion de R4 en Red va en una PR
de Alejandro despues de aceptar tu modulo.

## 4. Interfaz visual y conexion

Cada bloque siguiente tiene su propia Issue y rama nueva desde `main`:

| Rama sugerida | Resultado revisable |
| --- | --- |
| `catalina/tema-web` | Variables de tema, layout adaptable, titulo en espanol e identificacion de proyecto academico |
| `catalina/consultas-web` | Componentes Consultas para R1 R2 R3 R4 R6, con carga, vacio y error |
| `catalina/viajes-web` | Componente Viajes para R5, mostrando rutas, paradas y transbordo sin inventar tiempos |
| `catalina/api-web` | Funciones api.js y rutas Flask de requisitos ya integrados |

No es necesario hacer estas cuatro ramas a la vez. Empieza cada una cuando su
resultado pueda probarse. Mientras falte el motor, usa ejemplos en tu componente
con etiqueta visible `Datos de ejemplo`. Retira esos ejemplos al conectar la API.

Daniel entrega sus componentes y estilos en carpetas propias. Tu los montas en
App y mantienes el contador `versionRed`; no reescribes su carpeta. Publica en
una Issue los colores y variables antes de pedirle que ajuste sus pantallas.

Flask mantiene una Red para toda la sesion y delega reglas al motor. Usa los
nombres, rutas y respuestas de `CONTRATOS.md`; no hagas `fetch` a una direccion
absoluta en cada componente. `GET /api/estado` sigue siendo salud del servidor.
Al editar la API, prueba tambien peticiones invalidas y errores controlados.

Para las pantallas revisa con teclado, ventana angosta y zoom: etiquetas de
campos, foco visible, contraste, mensajes legibles, estados deshabilitados,
ausencia de desbordamientos y resultados claros. No se requiere comprar iconos,
mapas, fuentes ni servicios. No anuncies que es una app oficial de TransMilenio.

## 5. Conversion de datos

Rama sugerida `catalina/conversion-gtfs`, independiente de la interfaz.

1. Identifica y registra el enlace exacto del GTFS de julio de 2021 indicado
   por el curso. Si no se consigue, registra la limitacion; no sustituyas otra
   fecha sin avisar. No asumas que los CSV ya presentes prueban su procedencia.
2. Escribe `conversion/convertir_gtfs.py` y `conversion/README.md`. Entradas:
   ruta del ZIP y carpeta de salida; sin rutas personales fijas. Valida el ZIP
   y no lo extraigas sobre el repositorio sin controlar nombres de archivo.
3. Define un dia de servicio representativo usando calendario y excepciones.
   Justifica si incluyes solo troncales u otro alcance. No juntes todos los
   servicios de varios dias para afirmar que son buses por dia.
4. Relaciona stops, routes, trips y stop_times. Identifica sentidos y patrones de
   recorrido, normaliza estaciones sin fusionar ubicaciones distintas por un
   nombre ambiguo, y reporta colisiones. No unas plataformas por intuicion.
5. Conserva eventos de buses diferentes y horas mayores de 23. Documenta como
   conviertes segundos a minutos; no elimines eventos por compartir `HH:MM`.
6. Genera exactamente los tres CSV con los encabezados del contrato y escribe
   un informe de filas, referencias descartadas y decisiones. Incluye una prueba
   pequena de conversion y comprobacion de integridad.
7. Valida primero los CSV de la carpeta superior: formato, unicidad, referencias
   y horas. Solo incorporalos a `datos/` si la procedencia y las reglas coinciden.

No subas el ZIP grande como parte de un commit habitual. Incluye instrucciones
reproducibles para obtenerlo y convertirlo. Los CSV generados si forman parte de
la entrega. Si la conversion requiere una libreria nueva, se registra en una
lista separada dentro de `conversion/`, sin obligar al profesor a instalarla
para importar `motor`.

## 6. Antes de entregar cada PR

- Pruebas de R4 o conversion, segun corresponda.
- Para cambios web, `npm --prefix frontend run build` y revision en navegador.
- Para cambios API, pruebas con el cliente de Flask y la conexion real.
- Solo archivos de tu tarea, `main` incorporado y decision R12 actualizada.
- Tras integrar, regresa a `main` y actualiza antes de crear otra rama.

## 7. Sustentacion y aporte

Debes explicar busqueda binaria, construccion y limites de tu indice, conversion
de tiempos y frontera entre Flask y motor. Practica explicar R7 o R9 con
Alejandro. Actualiza `integrantes.md` con referencias a aportes integrados, en
una PR corta, sin atribuirte codigo de los demas por haberlo conectado a App.
