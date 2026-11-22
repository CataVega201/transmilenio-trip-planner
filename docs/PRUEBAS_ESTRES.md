# Comprobación de estrés y rúbrica — 21 de noviembre de 2026

## Resultados reproducidos

- 208 pruebas del proyecto y 2 del conversor aprobadas, sin omisiones.
- 10.000 cambios aleatorios en una red aislada de 80 estaciones, 20 rutas y
  eventos duplicados/horas extendidas. Comparación con una referencia independiente
  de listas y diccionarios fuera del motor. Se verifica cada resultado de cambio,
  autocompletado, rango, ranking y próximo bus, además de viajes cada diez pasos,
  recorridos, estados y deshacer/rehacer. No hubo discrepancias.
- R10 con 1.000.000 de pasajeros ordenados: 0,760 s. Con 300.000 llegadas
  desordenadas: 1,142 s. Ambos resultados completos coinciden con otra referencia.
- HTTP local con Waitress: 2.000 solicitudes, 16 clientes concurrentes, cero fallos,
  0,89 s total; mediana 4,5 ms y percentil 95 de 18,5 ms. Incluye consultas,
  cierres/reaperturas y simulación. Tras reabrir la estación de prueba, ranking
  y autocompletado coincidieron con el estado inicial.
- Sitio público: 32 solicitudes acotadas con cuatro clientes, cero fallos,
  mediana 239,2 ms. Consultas y simulación; se conservaron las estaciones públicas.
- Cliente y Operador comprobados a 1440, 390 y 320 px, sin desbordamiento.
  Cambiar de vista conserva los resultados de simulación. Las herramientas
  del operador están ocultas en la vista Cliente.
- Lint, compilación y npm audit correctos, sin avisos de vulnerabilidad.

Las cifras de tiempo corresponden al equipo y momento de la ejecución. Las
pruebas intensivas se hicieron en una instancia aislada. El plan público gratuito
tiene otros recursos y no se extrapola su capacidad desde el resultado local.

Para repetir la secuencia aleatoria en Command Prompt:

```cmd
set TM_ESTRES_PASOS=10000
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_estres_red.py -v
```

Sin esa variable la prueba usa 1.000 pasos para las comprobaciones habituales.

## Contraste con la rúbrica

| Criterio | Evidencia |
| --- | --- |
| motor/, frontend/, README e integrantes.md | Presentes y revisados |
| Firmas y formatos R1–R10 | Firmas verificadas; pruebas funcionales, de tipos de salida y casos borde |
| Prohibidos dentro de motor/ | Revisión AST de todos los módulos: sin dict/set, ordenamientos de biblioteca, min/max ni index/count; imports internos y csv |
| Red externa con nombres inventados y filas mezcladas | Pruebas de integración, referencias aleatorias y generador R11 |
| Decisiones y O grande | README y documentos R1–R10, con variables y alternativas |
| R11 | Panel con datos reales; cuatro tamaños y cinco repeticiones en el JSON del contrato completo |
| Historial de todo el grupo | Commits de los cuatro integrantes distribuidos en ocho días |
| URL pública y arranque | App desplegada y comando iniciar.py documentados |
| Sustentación, 3 puntos | Requiere que cada integrante explique cualquier requisito; no la verifica una prueba de software |
| Bonos de creatividad y motor | Dependen de la votación y comparación con otros grupos |

El enunciado original distingue usuarios y operadores por sus necesidades; la
rúbrica de entrega no exige cuentas ni contraseñas. Se agregó un selector de
vistas. La aplicación académica conserva una red compartida en memoria:
cualquiera puede seleccionar Operador y las operaciones siguen siendo públicas.

## Crecimiento observado

En docs/mediciones/2026-11-21-contrato-completo.json están las 68 filas de
10.000, 20.000, 40.000 y 80.000 estaciones, con cinco repeticiones.
La pendiente log-log de R10 ordenado es 1,07; desordenado, 1,19; carga, 1,18.
Las consultas con salida acotada y cambios tienen pendientes cercanas a cero
en esa red, coherentes con costos constantes o logarítmicos. En R7 el costo
del recorrido depende de L (paradas de la ruta), no solo del total de estaciones.
R5 tiene pruebas funcionales y no participa en la comparación de crecimiento.
Estos datos no predicen el bono frente al script y las redes del profesor.
