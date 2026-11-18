# Guia de Daniel Rincon

Tu enfoque principal es frontend: operacion de la red, simulacion y panel.
Implementas R10 en Python y la infraestructura que une las mediciones y pruebas.
No tienes que implementar los algoritmos de los demas para poder mostrar sus datos.

## 1. Prepararte

Sigue [INSTALACION.md](../INSTALACION.md), [Git paso a paso](../GIT_PASO_A_PASO.md)
y [CONTRATOS.md](../CONTRATOS.md). Usa tu cuenta, correo verificado y copia local.
Comprueba la pagina y Flask antes de tocar codigo.

## 2. Archivos propios

- `motor/fila.py`, `tests/test_fila.py`, `docs/decisiones/R10.md`.
- `frontend/src/components/operacion/`, `simulacion/` y `rendimiento/`.
- `rendimiento/`: generadores sinteticos y medicion del motor fuera de la web.
- `tests/integracion/` y su `__init__.py` para descubrimiento de pruebas.
- `iniciar.py`: futuro comando unico de arranque.
- `.github/` para futura automatizacion, mediante una tarea separada acordada.

No edites App.jsx, estilos globales, servidor.py, api.js ni archivos de
dependencias mientras Catalina los integra. Pide el cambio necesario en una
Issue. Usa estilos locales con prefijos `operacion-`, `fila-` y `rendimiento-`.

## 3. Primera tarea R10 independiente

Abre y asignate la Issue `R10 - Simular fila de abordaje`, indicando archivos,
interfaz acordada y pruebas. Desde `main` actualizado y limpio crea:

```cmd
git switch -c daniel/r10-fila
```

1. Crea `motor/fila.py` con la funcion suelta `simular_fila(llegadas, frecuencia,
   capacidad)`. No la pongas dentro de Red ni importes Flask.
2. Implementa una cola propia, por ejemplo un arreglo circular con crecimiento
   amortizado, si encaja con el algoritmo elegido. Otra implementacion debe
   justificarse. No uses `collections.deque`, `pop(0)` repetido ni busquedas
   lineales para sacar al primer pasajero.
3. Avanza por llegadas y salidas utiles; no simules cada minuto vacio. Conserva
   el orden FIFO y la regla de llegada antes de salida en un mismo instante.
4. Crea `tests/test_fila.py` con `unittest`. Compara la salida con calculos
   manuales pequenos antes de probar cientos de miles de pasajeros.
5. Completa `docs/decisiones/R10.md`: complejidad segun pasajeros, crecimiento
   del arreglo y espacio inevitable de salida.

Pruebas: los dos ejemplos del contrato; lista vacia; una llegada en cero;
personas simultaneas; cupo exacto; una mas que el cupo; varias salidas; gran
salto de tiempo; capacidad/frecuencia cero o negativas; llegadas desordenadas.

```cmd
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_fila.py" -v
```

Debe ejecutar pruebas y mostrar `OK`. Haz commits de avances coherentes,
prepara solo los archivos de R10 y sube `daniel/r10-fila` con `git push -u
origin daniel/r10-fila`. Abre PR y pide revision a Mariana. La exportacion final
en `motor/__init__.py` la integra Alejandro cuando exista tu modulo.

## 4. Tus tres pantallas

Una Issue y una rama por bloque, empezando siempre desde `main` actualizado:

| Rama sugerida | Entrega |
| --- | --- |
| `daniel/operacion-web` | `Operacion.jsx` con R7 R8 R9 y recorrido en ambos ordenes |
| `daniel/simulacion-web` | `Simulacion.jsx` con R10 y resumen legible de abordaje y espera |
| `daniel/rendimiento-web` | `Rendimiento.jsx` con R11 y explicaciones junto a las graficas |

Cada componente exporta por defecto su nombre acordado y usa CSS propio. No
modifica App para montarse: entrega el import y ejemplo de uso en la PR para
que Catalina lo integre. En Operacion llama a `onCambio` tras cambios exitosos
para refrescar consultas y viajes. No declares un cierre exitoso antes de la
respuesta real del servidor.

Mientras falte la API puedes mostrar ejemplos en tu carpeta con etiqueta visible
`Datos de ejemplo`. No crees endpoints ficticios permanentes. Cuando Catalina
publique `api.js`, usa sus funciones y elimina la simulacion local de la red.

Todas las pantallas deben tener carga, error, vacio y exito. Distingue que no
quedan acciones por deshacer de un fallo del servidor. Una estacion cerrada se
puede mostrar al operador para reabrirla, aunque no aparezca como opcion al viajero.
En simulaciones grandes no renderices cientos de miles de filas a la vez: usa
resumen y una muestra claramente identificada o paginacion, conservando el
resultado completo del motor para las pruebas.

## 5. Infraestructura R11

Rama sugerida `daniel/mediciones-r11`. Los generadores y el recolector van en
`rendimiento/`, fuera de `motor/`. Cada responsable te entrega la operacion a
medir, preparacion, variables de tamano y complejidad esperada; tu ensamblas.

1. Genera carpetas temporales con los tres CSV y tamanos crecientes, sin nombres
   de la red real. Usa una semilla fija para comparar ensayos.
2. Separa carga, preparacion, calentamiento y tiempo de la operacion. Usa
   `time.perf_counter_ns`, repeticiones y mediana. No midas red HTTP como si
   fuera el costo de busqueda del motor.
3. Mide todos los metodos evaluables: R1 R2 R3 R4 R6 R7 R8 R9 R10 y carga.
   R7 incluye agregar, quitar y ambos recorridos; R8 ambos estados; R9 ambas
   direcciones. R5 se comprueba funcionalmente y se etiqueta aparte.
4. Para cambios y deshacer, restaura el escenario entre ensayos fuera del tramo
   medido. No midas miles de cierres de una estacion que ya quedo cerrada.
5. Presenta resultados con operacion, tamano y unidad de n, k si aplica,
   repeticiones, mediana en ns y relacion con el tamano anterior. Indica cache
   fria/caliente, tamano de salida y explicacion del autor.
6. Acuerda con Catalina el esquema JSON exacto de R11 y limites razonables de
   trabajo por peticion antes de conectar `medirRendimiento`.

El panel debe generar mediciones reales en Python al solicitarlo. No usar curvas
inventadas ni recalcular todo en cada pulsacion de tecla. No prometer relaciones
exactas de 2 o 4 cuando los tiempos pequenos tienen ruido.

## 6. Pruebas de integracion y arranque

Rama `daniel/integracion` cuando Red tenga metodos integrados: crea una red
pequena en directorio temporal dentro de tus pruebas; usa `unittest`, `tempfile`
y `csv` fuera del motor. Asegura cierre, reapertura, edicion, consultas, ranking,
viajes e historial coherentes. Usa nombres distintos de los CSV reales.

```cmd
.\.venv\Scripts\python.exe -m unittest discover -s tests/integracion -p "test_*.py" -v
```

Para `iniciar.py`, acuerda primero con Catalina como Flask servira la pagina
compilada. La entrega prevista es un lanzador que verifica dependencias,
compila React y sirve `dist` junto con API en un unico servidor local. No necesitas
mantener dos servidores de desarrollo en el comando final. Esa integracion
requiere una PR pequena de Catalina en servidor.py antes o junto a la tuya.

El comando final previsto, TODAVIA NO DISPONIBLE, es:

```cmd
.\.venv\Scripts\python.exe iniciar.py --datos datos
```

Debe aceptar otra carpeta de datos, funcionar aunque la ruta tenga espacios y
mostrar errores claros si faltan dependencias o CSV. No instalar programas ni
librerias silenciosamente durante el arranque. Se prueba en una copia nueva y
se actualiza el README solo cuando funcione. Las instalaciones iniciales quedan
documentadas aparte; no son necesarias en cada ejecucion.

## 7. Revision y sustentacion

Compila cada cambio de pantalla con `npm --prefix frontend run build` y revisa
ventana angosta, teclado, errores y resultados. Para R10, mide cantidades
crecientes de pasajeros y memoria; no ocultes la salida completa al evaluar.
Explica cola, FIFO y saltos de eventos. Practica R2/R3 con Mariana para la
sustentacion. Registra tus PR integradas en integrantes.md en una tarea corta.
