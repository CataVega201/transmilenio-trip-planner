# Validacion y conversion de datos

Responsable: Catalina Vega. El conversor GTFS esta pendiente. Actualmente solo
existe un validador de los tres CSV; no modifica ni corrige los archivos.

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

## Pendientes

Obtener o identificar el GTFS fuente y, si existe, el script que produjo los
CSV actuales. Definir dia de servicio, sentidos, patrones y normalizacion con
esa evidencia. Implementar la conversion reproducible y sus pruebas antes de
presentar estos archivos como datos definitivos de entrega.

Este codigo vive fuera de motor/: usa diccionarios y conjuntos para validar
datos, tal como permite el enunciado fuera del motor. No debe importarse desde
motor/ para resolver los requisitos del curso.
