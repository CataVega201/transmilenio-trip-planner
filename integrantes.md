# Integrantes y responsabilidades

Este es el reparto aprobado. Una responsabilidad asignada no significa que el
trabajo este hecho. Cada persona conserva la autoria de sus cambios reales.

| Integrante | Motor | Otras responsabilidades |
| --- | --- | --- |
| Catalina Vega | R4; carga y Red; R5; integración R8/R9 | Diseno base; consultas y viajes en la web; conexion Flask; conversion GTFS; integracion de componentes |
| Daniel Rincon | R10 fila de abordaje | Pantallas de operacion y simulacion; panel R11; mediciones comunes; pruebas de integracion; arranque con un comando |
| Mariana Parra | R1 busqueda; R2 autocompletado; R3 rangos; R6 ranking | Indices de estaciones; tabla hash compartida; pruebas y decisiones propias |
| Alejandro Curtidor | Módulos R7 rutas y R9 historial | Pruebas y decisiones de esos módulos; integración restante reasignada a Catalina |

Todos aportan pruebas, mediciones y justificaciones R12 de su parte. Daniel
ensambla el panel; no tiene que descubrir ni escribir las decisiones de todos.
Todos deben poder explicar un requisito ajeno para la sustentacion.

## Aportes comprobados al preparar estas guias

- Catalina: configuracion de archivos ignorados (`e70a636`), base React y Vite
  (`8d6145b`), servidor Flask y conexion web (`44c5e03`).
- Catalina, integrado: índice R4 y pruebas ([PR #3](https://github.com/CataVega201/transmilenio-trip-planner/pull/3)), conversión real y validación ([PR #4](https://github.com/CataVega201/transmilenio-trip-planner/pull/4)), tema visual (c34934b) y consultas y viajes ([PR #6](https://github.com/CataVega201/transmilenio-trip-planner/pull/6)).
- Daniel, integrado: R10 fila de abordaje con cola FIFO propia, pruebas y decisión ([PR #8](https://github.com/CataVega201/transmilenio-trip-planner/pull/8)); pantalla de simulación ([PR #18](https://github.com/CataVega201/transmilenio-trip-planner/pull/18)); pantalla de operación con R7, R8 y R9 ([PR #19](https://github.com/CataVega201/transmilenio-trip-planner/pull/19)).
- Daniel, integrado: infraestructura de mediciones R11 ([PR #13](https://github.com/CataVega201/transmilenio-trip-planner/pull/13)), arranque único `iniciar.py` y pruebas de integración ([PR #20](https://github.com/CataVega201/transmilenio-trip-planner/pull/20)) y panel de rendimiento ([PR #21](https://github.com/CataVega201/transmilenio-trip-planner/pull/21)).
- Mariana, integrado: tabla hash compartida ([PR #9](https://github.com/CataVega201/transmilenio-trip-planner/pull/9)) y estado de estaciones R1 ([PR #12](https://github.com/CataVega201/transmilenio-trip-planner/pull/12)). R2, R3 y R6 siguen pendientes de publicación.
- Alejandro, integrado: recorridos y edición de rutas R7 ([PR #15](https://github.com/CataVega201/transmilenio-trip-planner/pull/15)) y pilas de historial R9 ([PR #17](https://github.com/CataVega201/transmilenio-trip-planner/pull/17)).

## Registro posterior

Cada persona agregara aqui una referencia a sus PR integradas y que hizo.
Como este archivo es compartido, se cambia en una PR corta independiente,
despues de actualizar la rama con `main`. No se inventan aportes ni se cambia
la identidad de Git para simular que trabajo otra persona.

El reparto se revisara tras la primera ronda: Alejandro concentra las
dependencias del motor y Catalina asume tambien datos e integracion. Si una
parte crece, se reasigna una tarea concreta y su archivo antes de empezarla.

## Reasignación de integración

Catalina asume la carga CSV, la fachada Red, viajes R5 y la coordinación de cierres con historial R8/R9 por disponibilidad del equipo el día de entrega. Reutiliza los módulos de rutas e historial y sus commits originales de Alejandro, el índice de estaciones de Mariana y la simulación de Daniel. R2/R3/R6 siguen asignados a Mariana.

Integración de Catalina verificada y fusionada en [PR #26](https://github.com/CataVega201/transmilenio-trip-planner/pull/26). Los ajustes de integración posteriores conservan los commits originales de cada integrante.
