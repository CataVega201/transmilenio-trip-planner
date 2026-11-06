# Guia de Mariana Parra

Tu enfoque es el motor de estaciones y consultas: R1, R2, R3 y R6. Tus indices
deben trabajar con otra red mas grande y reflejar cierres y reaperturas, no solo
pasar pruebas con los CSV reales.

## 1. Prepararte

Sigue [INSTALACION.md](../INSTALACION.md), [Git paso a paso](../GIT_PASO_A_PASO.md)
y [CONTRATOS.md](../CONTRATOS.md). Usa tu cuenta e identidad. No hace falta saber
React para empezar, pero instala la base para poder comprobar la app completa.

## 2. Archivos propios y limites

- `motor/tabla_hash.py`, `motor/estaciones.py`, `motor/indice_alfabetico.py`,
  `motor/ranking.py`.
- `tests/test_tabla_hash.py`, `tests/test_estaciones.py`, `tests/test_ranking.py`.
- `docs/decisiones/R1.md`, `R2.md`, `R3.md`, `R6.md`.

No edites `motor/red.py` ni `motor/__init__.py`: Alejandro integra la fachada.
No edites servidor.py para comprobar tus funciones; usa pruebas Python directas.
Tu modulo mantiene el estado unico abierto/cerrado. Alejandro lo consulta para
viajes y coordina cambios e historial; no mantengan dos banderas independientes.

## 3. Primera tarea tabla hash

Abre la Issue `Base - Tabla hash del motor`, asignatela, lista archivos y confirma
la interfaz prevista. Con `main` actualizado y estado limpio crea:

```cmd
git switch -c mariana/tabla-hash
```

1. Crea una tabla hash propia en `motor/tabla_hash.py`, con los metodos
   `guardar`, `obtener`, `eliminar` y `pares` del contrato. No uses dict o set ni
   siquiera para la estructura auxiliar, colisiones o pruebas internas del modulo.
2. Elige y explica manejo de colisiones, funcion hash, factor de carga y
   crecimiento. Usa arreglos y tus propios nodos o posiciones segun tu decision.
3. Prueba insercion, reemplazo, clave ausente, eliminacion, colisiones forzadas,
   redimensionamiento, muchas claves y valores que sean None. `obtener` usa el
   argumento defecto para distinguir ausente cuando un consumidor lo necesite.
4. Crea `tests/test_tabla_hash.py`. Las pruebas estan fuera del motor y pueden
   usar herramientas de comparacion que el motor tiene prohibidas.

```cmd
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_tabla_hash.py" -v
```

Haz commit y sube la rama con `git push -u origin mariana/tabla-hash`. Pide
revision a Alejandro. Entrega esta base pronto: R4 y el almacen de rutas pueden
reutilizarla despues de integrarse. No es necesario esperar a terminar R1 a R6.

## 4. Consultas de estaciones

Una Issue y rama por bloque. Sugerencias:

| Rama | Resultado |
| --- | --- |
| `mariana/estado-r1` | `IndiceEstaciones`, estado exacto y casos ausente/abierta/cerrada |
| `mariana/alfabetico-r2-r3` | Indice ordenado, autocompletado y rango con cierres coherentes |
| `mariana/ranking-r6` | Ranking con conteos correctos y estrategia de actualizacion |

R1 necesita acceso frecuente por nombre: compara tabla hash con busqueda lineal.
R2/R3 necesitan orden: estudia un arbol balanceado, trie con recorrido ordenado
u otra estructura del curso. Una estructura para R1 no obliga a usar la misma
para todo. Justifica insercion, cierre/reapertura, rango y salida.

Probar que el resultado esta ordenado no demuestra que sea eficiente. Ordenar
toda la red en cada pulsacion o buscar un prefijo recorriendo todas las estaciones
puede incumplir el objetivo. Tampoco ignores el costo de saltar estaciones
cerradas en un indice que las conserva. Documenta las variables reales.

Antes de cerrar este bloque acuerda con Alejandro una operacion
`cambiar_estado(nombre, abierta)` que actualice todas tus estructuras sin
generar su propia accion de historial. Su fachada es quien registra la accion.
El camino de deshacer debe reutilizar la misma actualizacion de indices.

## 5. Ranking R6

Cuenta eventos diarios de horarios vigentes, no rutas distintas ni visitas al
frontend. Las estaciones abiertas con cero buses tambien pueden aparecer al
pedir un k grande. Empates por nombre.

Compara guardar un orden reutilizable frente a calcular/ordenar desde cero en
cada consulta. Una cache puede mejorar consultas repetidas, pero hay que medir
cuando cambia la red. Acuerda actualizaciones por cierre, reapertura y edicion
de ruta con Alejandro. No des por buena una reconstruccion completa de todos
los conteos en cada cambio sin medir el costo total.

La interfaz inicial `actualizar(filas)` es provisional; si una actualizacion
incremental es necesaria, propon la firma concreta en la Issue de contratos y
coordina el cambio con Alejandro antes de implementarla. No cambies el formato
publico `[nombre, cantidad_buses]` para acomodar la estructura interna.

## 6. Pruebas minimas de tu bloque

- Red vacia, una estacion, nombres con prefijos comunes y normalizacion.
- R1 ausente, abierta y cerrada; no confundir cerrada con inexistente.
- R2 prefijo vacio, sin coincidencias, k cero/negativo/grande, limite exacto.
- R3 extremos iguales, extremos incluidos, desde mayor que hasta, sin resultados.
- R6 empates, ceros, k mayor que el total, duplicados de horario que representan
  buses distintos, cambios de pertenencia a rutas.
- Cerrar y reabrir debe modificar autocompletado, rangos y ranking; luego lo
  mismo mediante deshacer y rehacer en pruebas de Red con Alejandro y Daniel.

Comandos despues de crear los archivos correspondientes:

```cmd
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_estaciones.py" -v
```

```cmd
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_ranking.py" -v
```

## 7. Mediciones, entrega y sustentacion

Entrega a Daniel un escenario por operacion con el significado de n y k, datos
de preparacion y Big O. Distingue construir indices de consultar; en rango y
autocompletar controla cantidad de resultados. Para tabla hash explica costo
esperado y peor caso; para arboles demuestra que mantienen su propiedad.

Cada PR lleva solo archivos propios, pruebas reales y su decision R12. No
esperes a terminar todo para subir tus aportes. Tras integrar actualiza tu
registro en integrantes.md en PR corta. Practica explicar R10 con Daniel y R7
con Alejandro; no basta memorizar las estructuras de tus propios requisitos.
