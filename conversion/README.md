# Validacion y conversion de datos

Responsable: Catalina Vega. El conversor lee un ZIP GTFS estático y genera los tres CSV en una carpeta nueva. Usa Python sin instalaciones adicionales.

## Ejecutar el conversor

Desde la raíz del repositorio, sustituye la ruta del ZIP y la fecha por las del servicio que quieras convertir. Esta fecha es un ejemplo.

```cmd
.\.venv\Scripts\python.exe conversion/convertir_gtfs.py "ruta al archivo.zip" datos_generados --fecha 2021-07-01
```

Selecciona todos los viajes activos del día según calendar.txt y calendar_dates.txt. El alcance incluye todas las rutas activas del archivo. Usa la estación padre cuando existe, normaliza nombres y separa sentidos y variantes de paradas. El identificador combina route_id, direction_id (X si falta) y número de patrón. Cada evento usa la hora de salida o, si falta, la de llegada. Descarta los segundos y conserva las horas superiores a 23. Valida los resultados antes de crear la carpeta definitiva.

Esta versión requiere horarios explícitos. Si encuentra servicios por frecuencia, horas sin especificar, estaciones ambiguas o un recorrido que repite una estación, se detiene con un mensaje. El equipo deberá decidir cómo representar esos casos si aparecen en el archivo histórico. La fecha exacta y el alcance usados para los CSV del profesor siguen pendientes de verificar.

La prueba crea un ZIP temporal y ejecuta el mismo comando del usuario. Cubre calendario y excepciones, dos sentidos, estación padre, orden numérico, horas extendidas y protección de una salida existente. Referencia de los campos: [GTFS Schedule](https://gtfs.org/documentation/schedule/reference/).

```cmd
.\.venv\Scripts\python.exe -m unittest discover -s conversion -p "test_*.py" -v
```

Desde la raiz del repositorio, para revisar los archivos de la carpeta superior:

```cmd
.\.venv\Scripts\python.exe conversion/validar_csv.py ..
```

Sustituye `..` por la carpeta que contiene los CSV; usa comillas si tiene espacios.
No requiere librerias externas. Salida JSON; codigo 0 sin problemas, 1 si detecta
datos incompatibles con los acuerdos y 2 si no puede leer los archivos.

Comprueba encabezados, columnas, normalizacion de nombres, estaciones unicas,
referencias, ordenes positivos y unicos, paradas repetidas por ruta y horas.
La regla de una parada por ruta es un acuerdo propuesto del equipo: los bucles
GTFS necesitan una politica explicita. Las filas de horarios repetidas se
cuentan y se conservan. Saltos en la numeracion y parejas sin horarios se
informan como estadisticas, no como errores fatales.

## Inspeccion inicial de los CSV existentes

Procedencia declarada por Catalina: los tres CSV fueron enviados por el
profesor a traves de Teams. No se recibio el ZIP GTFS ni un script o enlace
de conversion. Son los datos suministrados para el curso; no son una conversion
realizada por este equipo. La fecha y el dia de servicio exactos no se han
comprobado contra un GTFS fuente.

Resultado de la revision local del 5 de noviembre de 2026:

| Dato | Resultado |
| --- | --- |
| Estaciones unicas | 147 |
| Rutas | 181 |
| Paradas en recorridos | 1927 |
| Registros de horarios | 140492 |
| Filas identicas adicionales de horarios | 1580 |
| Horarios con hora mayor o igual a 24 | 0 |
| Primer y ultimo minuto observado | 1 y 1439 |
| Parejas ruta-estacion sin horarios | 0 |
| Estaciones sin ruta | 0 |
| Problemas detectados por el validador | 0 |

Esto acredita consistencia estructural, no cobertura de la red,
fecha ni exactitud de los horarios. Los duplicados pueden ser buses diferentes;
no se eliminan sin consultar el GTFS. La ausencia de horas extendidas tampoco
demuestra que el origen no las tuviera: podria existir una transformacion previa.

El validador se comprobo adicionalmente con una red temporal valida, eventos
duplicados, horas 25:10 y errores deliberados de referencia y minutos.

## Reproducción con el GTFS histórico

Se verificó el [GTFS del 14 de julio de 2021](https://storage.googleapis.com/gtfs-estaticos/GTFS-2021-07-14.zip) publicado en el almacenamiento del operador. Tamaño 56.688.605 bytes (54,1 MiB). SHA-256 del ZIP: `4ffc631354184c0994679dcda380603facfd5810d9d153ef9d83fed449059ff2`. Se eligió una fecha de servicio coincidente con esa publicación. También existe un archivo del 26 de julio. El material del curso no precisa cuál usó el profesor.

Para repetir la ejecución, descarga el ZIP y elige una carpeta de salida nueva:

```cmd
.\.venv\Scripts\python.exe conversion/convertir_gtfs.py "%USERPROFILE%\Downloads\GTFS-2021-07-14.zip" comprobacion_julio --fecha 2021-07-14 --troncal
.\.venv\Scripts\python.exe conversion/validar_csv.py comprobacion_julio
```

El modo `--troncal` usa las rutas clasificadas como TRONCAL por el archivo histórico. Sin estación padre, reconoce sufijos de plataforma como «C - 2 ó 5» o «T9». Dos plataformas consecutivas de una misma estación y viaje cuentan como una visita con la última salida. La agrupación por nombre es una decisión de conversión para este feed. Una visita no consecutiva repetida detiene la conversión. Cada secuencia de paradas distinta conserva su propio identificador para ofrecer solo viajes en el sentido real.

`datos_generados/` contiene la salida real que validamos: 147 estaciones, 264 patrones de ruta, 2599 paradas en recorridos y 140532 eventos. `datos/` contiene los tres archivos enviados por Teams: 147 estaciones, 181 rutas y 140492 eventos. La coincidencia en cantidad de estaciones no demuestra una conversión idéntica. El script del profesor y sus criterios de selección siguen sin conocerse. El motor podrá recibir cualquiera de estas carpetas.

Este codigo vive fuera de motor/: usa diccionarios y conjuntos para validar
datos, tal como permite el enunciado fuera del motor. No debe importarse desde
motor/ para resolver los requisitos del curso.
