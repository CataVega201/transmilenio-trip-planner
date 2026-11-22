# Planeador de viajes TransMilenio

Proyecto de Estructuras de Datos y Algoritmos de Catalina Vega, Mariana Parra,
Alejandro Curtidor y Daniel Rincon.

## Empieza aqui

**Para empezar con ChatGPT, usa las [guías rápidas del equipo](docs/inicio/LEEME.md).** Incluyen instalación, prompts y tareas individuales.

- [Guia general del equipo](docs/GUIA_GENERAL.md)
- [Instalacion desde cero](docs/INSTALACION.md)
- [Git y GitHub paso a paso](docs/GIT_PASO_A_PASO.md)
- [Acuerdos del motor y de la conexion web](docs/CONTRATOS.md)
- [Responsabilidades y aportes](integrantes.md)
- Guias personales: [Catalina](docs/miembros/CATALINA.md),
  [Daniel](docs/miembros/DANIEL.md), [Mariana](docs/miembros/MARIANA.md)
  y [Alejandro](docs/miembros/ALEJANDRO.md).

## Estado real del proyecto

La app integra estado de estaciones, próximo bus, viajes, edición de rutas,
cierres e historial, simulación y panel de rendimiento. Se puede iniciar con un
comando. R2 (autocompletar), R3 (rangos) y R6 (ranking) siguen pendientes del
código de Mariana. Esas consultas devuelven 503 con una explicación y sus
pruebas integrales dependientes se omiten explícitamente hasta integrarlas.

## Ejecutar la app

Sigue primero [la instalación](docs/INSTALACION.md), instala las dependencias
de Python y del frontend y ejecuta desde la carpeta del proyecto:

```cmd
.\.venv\Scripts\python.exe iniciar.py --datos datos
```

El comando compila el frontend y sirve página y API en un mismo servidor.
Para omitir la apertura del navegador usa `--no-abrir`. Para cambiar el puerto
usa `--puerto 5001`. `--sin-compilar` reutiliza una compilación existente.

Desarrollo con recarga automática en dos terminales:

```cmd
.\.venv\Scripts\python.exe servidor.py
npm --prefix frontend run dev
```

## Decisiones del curso R12

Todas las operaciones están en motor/. Las búsquedas por nombre normalizan la
clave y conservan el nombre original del CSV. Las tablas hash son propias y sus
costos constantes son esperados; con colisiones pueden llegar a O(n).

| Req. | Estructura y decisión | Costo y variables | Alternativa considerada |
| --- | --- | --- | --- |
| R1 | Tabla hash con registro de nombre original y estado | O(1) esperado, O(n) peor caso; n estaciones | Buscar linealmente costaría O(n) |
| R2/R3 | Pendiente el índice alfabético de Mariana | Sin complejidad final acreditada | Comparar árbol balanceado o trie con recorrido ordenado |
| R4 | Arreglos de horarios por pareja y búsqueda binaria | O(log h) consulta; O(h log h) preparar cada grupo de h eventos | Barrer h horarios en cada consulta |
| R5 | Mejor primer tramo en tabla hash y recorrido inverso desde destino | O(S + P) esperado; S/P son las paradas recorridas desde ambos extremos; espacio O(u) para u estaciones alcanzables | Probar todas las parejas de rutas repite recorridos |
| R6 | Pendiente el índice incremental de ranking | Sin complejidad final acreditada | Comparar índice ordenado con ordenar todos los conteos por consulta |
| R7 | Listas doblemente enlazadas con índices hash | Insertar O(1) esperado amortizado; quitar O(d), d rutas de la estación; recorrido O(L), L paradas | Un arreglo desplaza elementos al editar |
| R8 | Estado único en el índice de estaciones; conteos y pertenencia vigentes | Cerrar/reabrir O(1) esperado, aparte de descartar rehacer | Reconstruir toda la red tras cada cierre |
| R9 | Dos pilas y registros mínimos que invierten el cambio exacto | O(1) esperado o O(d) según la acción; descartar a nodos de rehacer puede costar O(a), amortizado entre registros | Guardar una copia completa por acción multiplica memoria |
| R10 | Cola circular propia, merge sort estable y saltos entre eventos | O(n) con llegadas ordenadas, O(n log n) desordenadas; espacio O(n), n pasajeros | Simular cada segundo y desplazar la fila depende del horizonte y repite trabajo |

Detalles, invariantes y pruebas:

- [R1](docs/decisiones/R1.md), [R4](docs/decisiones/R4.md),
  [R5](docs/decisiones/R5.md), [R7](docs/decisiones/R7.md),
  [R8](docs/decisiones/R8.md), [R9](docs/decisiones/R9.md),
  [R10](docs/decisiones/R10.md).
- [Carga CSV y Red](docs/decisiones/CARGA_RED.md).
- [Tabla hash compartida](docs/decisiones/R12.md).
- [R11 y mediciones parciales](docs/decisiones/R11.md).

Para comprobar las pruebas:

```cmd
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe -m unittest discover -s conversion
```

Las pruebas de integración informan ocho omisiones por R2/R3/R6 pendientes.
No se consideran pruebas aprobadas. Los métodos restantes se comprueban con
redes inventadas, filas mezcladas, nombres originales y casos borde.

Todo el proyecto se desarrolla localmente. No requiere cuentas de IA, claves
de API, alojamiento ni servicios de pago para funcionar.

## Integración de Red

Se puede importar `Red` desde `motor` y cargar `Red("datos")` o
`Red("datos_generados")`. Ya están conectadas las consultas de estado,
horarios y viajes, edición de rutas, cierres, reaperturas y deshacer/rehacer.
R2, R3 y R6 dependen aún de los índices de Mariana y responden como módulos
pendientes en la API.

- [Carga y complejidad de construcción](docs/decisiones/CARGA_RED.md)
- [Viajes R5](docs/decisiones/R5.md)
- [Cierres e integración R8/R9](docs/decisiones/R8.md)

Pruebas de la integración: `python -m unittest discover -s tests`.
