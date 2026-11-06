# Guia de Alejandro Curtidor

Tu enfoque es el motor de rutas, viajes y cambios: R5, R7, R8 y R9. Integras la
clase Red usando modulos de tus companeros. Tu bloque tiene muchas conexiones;
por eso Catalina asume conversion y servidor, y Daniel las pruebas integrales
y mediciones comunes. Entrega piezas pequenas para no convertirte en un bloqueo.

## 1. Prepararte

Sigue [INSTALACION.md](../INSTALACION.md), [Git paso a paso](../GIT_PASO_A_PASO.md)
y [CONTRATOS.md](../CONTRATOS.md). Confirma especialmente politicas de cierres,
edicion, conteos y respuestas de viaje antes de programar esas partes.

## 2. Archivos propios

- `motor/__init__.py`, `motor/red.py`, `motor/carga.py`.
- `motor/rutas.py`, `motor/viajes.py`, `motor/historial.py`.
- `tests/test_red.py`, `test_rutas.py`, `test_viajes.py`, `test_historial.py`.
- `docs/decisiones/R5.md`, `R7.md`, `R8.md`, `R9.md`.

No reimplementes tabla hash, estaciones, horarios ni fila: sus autores los
entregan en archivos separados. No edites los modulos de Mariana para agregar
un cierre; acuerda y usa su interfaz. No importes Flask desde el motor.

## 3. Primera tarea R7 sin dependencias

Abre la Issue `R7 - Recorridos y edicion de rutas`, asignatela y confirma los
archivos. Desde `main` actualizado y limpio crea:

```cmd
git switch -c alejandro/r7-rutas
```

1. Crea la estructura de una ruta en `motor/rutas.py`. Considera lista doblemente
   enlazada para insercion, eliminacion y recorrido en ambos sentidos. Compara
   con arreglo y explica sus costos.
2. Empieza con una ruta pequena sin esperar a Red. Prueba primero nodos, enlaces
   de ida y vuelta, cabeza y cola. El acceso por nombre puede integrarse con la
   tabla hash de Mariana despues de su PR; no mantengas una tabla duplicada.
3. Crea `tests/test_rutas.py`. No basta verificar ida; cada mutacion debe dejar
   ida y vuelta coherentes, sin ciclos ni nodos perdidos.
4. Escribe `docs/decisiones/R7.md`. Diferencia el costo de modificar enlaces
   cuando ya tienes el nodo del costo de localizarlo y actualizar indices.

```cmd
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_rutas.py" -v
```

Prepara solo esos archivos, haz commit, sube la rama y pide revision a Catalina.
No crees un `__init__.py` que importe archivos todavia inexistentes.

## 4. Historial R9 como pieza independiente

Rama sugerida `alejandro/r9-historial`. Puedes construir y probar pilas propias
sin tener toda la red. Compara dos pilas con otras formas de guardar acciones.

Cada accion guarda datos suficientes para invertir el cambio exacto: estado
anterior, ruta, posicion y estacion segun la operacion. No hagas copia completa
de toda la red para cada cierre sin justificar tiempo y memoria.

La fachada registra una accion solamente cuando el cambio fue exitoso. Nuevo
cambio exitoso vacia rehacer; un fallo no lo vacia. Durante deshacer/rehacer se
aplica el cambio sin crear otra accion. No uses una llamada recursiva al metodo
publico que termine registrando la misma accion otra vez.

Prueba con acciones pequenas de ejemplo fuera del motor: orden LIFO, historial
vacio, varios deshacer/rehacer, cambio nuevo tras deshacer y accion sin efecto.
Integra cierres y rutas despues, cuando sus modulos esten listos.

## 5. Fachada Red y carga

Rama sugerida `alejandro/red-carga`. Espera que los modulos necesarios esten
integrados para importar sus implementaciones reales. Puedes entregar Red por
bloques, manteniendo los imports existentes utilizables.

- `Red(carpeta)` lee solo `estaciones.csv`, `rutas.csv`, `horarios.csv`, con
  `csv`, desde la carpeta recibida. No necesita `os` ni `pathlib` dentro del
  motor: construye rutas con operaciones de str o abre con una ruta relativa
  controlada a esa carpeta. No cambies el directorio global del proceso.
- No uses dict ni siquiera para guardar las filas leidas. `csv.reader` entrega
  listas; `csv.DictReader` introduce diccionarios y no debe usarse en el motor.
- Centraliza normalizacion en carga o un ayudante de un archivo propio, y acuerda
  su import con consumidores. Datos ya normalizados se pasan a los indices.
- Los ordenes de ruta y horarios no se suponen preordenados. Usa algoritmos
  propios y documenta la construccion. Detecta referencias y filas invalidas.
- Exporta las firmas oficiales desde `motor/__init__.py` una vez sus imports
  existan. No incluyas una app, un servidor ni una red global en ese archivo.
- Delega R1 R2 R3 R6 a Mariana; R4 a Catalina; R10 a la funcion de Daniel.
- Para R4 valida apertura y pertenencia vigente antes de consultar horarios.

En `tests/test_red.py` crea CSV pequenos en carpetas temporales desde el test,
fuera del motor. Los tres archivos deben poder cambiar de nombres de estaciones,
cantidad de rutas y orden de filas sin romper la implementacion.

## 6. Cierres R8 y cambios coordinados

Rama `alejandro/cierres-e-historial` cuando las piezas esten aceptadas.

`IndiceEstaciones` es la fuente unica de apertura. Al cerrar, se actualizan
indices consultables y ranking usando interfaces acordadas con Mariana. La
estacion permanece fisicamente en las rutas y no se puede usar para subir,
bajar ni transbordar. Los horarios fuente se conservan para poder reabrir.

Al insertar o quitar una parada, actualiza pertenencia e indices dependientes.
No inventes horarios para la nueva parada. Deshacer debe restaurar tanto el
recorrido como visibilidad, conteos y resultados. `recorrido(al_reves=True)`
solo muestra orden inverso: no crea viajes de regreso.

Coordina con Mariana el costo de mantenimiento antes de implementar; no le
pidas corregir su archivo mientras tu PR lo modifica tambien. Propongan en la
Issue una interfaz pequena y cada autor cambia sus archivos en su propia PR.

## 7. Viajes R5

Rama `alejandro/viajes-r5`. Usa el recorrido vigente y estaciones abiertas.
Enumera candidatos directos y con un transbordo, respeta sentido y minimiza
paradas segun el contrato. R5 no tiene medicion obligatoria de rendimiento,
pero debe funcionar para cualquier red valida.

No mezcles criterio de menos paradas con llegada mas temprana. El proyecto no
pide calcular viajes de dos transbordos ni garantizar conexiones por horario.
Implementa desempates deterministas sin `min`, `sorted` o estructuras prohibidas.

Prueba: directo; un transbordo; sin conexion; camino de regreso imposible;
empate; origen igual a destino; origen/destino cerrados; transbordo cerrado;
estacion intermedia cerrada que se atraviesa; ruta editada y luego deshecha.

## 8. Comprobaciones

Ejecuta los comandos cuando existan los archivos correspondientes:

```cmd
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_red.py" -v
```

```cmd
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_historial.py" -v
```

```cmd
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_viajes.py" -v
```

Comprueba firmas con una prueba de import cuando los dos exports esten listos:

```cmd
.\.venv\Scripts\python.exe -c "from motor import Red, simular_fila; print('Importacion correcta')"
```

Despues ejecuta la suite completa con Daniel. No cambies una salida solamente
para ajustar una prueba propia: revisa el acuerdo y corrige lo que este mal.

## 9. Entrega y sustentacion

Cada bloque tiene PR, pruebas y decision R12. Entrega a Daniel escenarios de
carga, agregar/quitar, ambos recorridos, cierre/reapertura y deshacer/rehacer,
incluyendo el costo de mantener indices. Los comentarios de codigo deben
explicar invariantes o decisiones, no repetir cada linea.

Practica explicar R4 con Catalina y R1/R2 con Mariana. Todos deben saber recorrer
el camino navegador-servidor-motor sin poner reglas del curso fuera de motor.
Actualiza tus aportes en integrantes.md despues de integrar cada bloque importante.
