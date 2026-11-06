# Integrantes y responsabilidades

Este es el reparto aprobado. Una responsabilidad asignada no significa que el
trabajo este hecho. Cada persona conserva la autoria de sus cambios reales.

| Integrante | Motor | Otras responsabilidades |
| --- | --- | --- |
| Catalina Vega | R4 proximo bus | Diseno base; consultas y viajes en la web; conexion Flask; conversion GTFS; integracion de componentes |
| Daniel Rincon | R10 fila de abordaje | Pantallas de operacion y simulacion; panel R11; mediciones comunes; pruebas de integracion; arranque con un comando |
| Mariana Parra | R1 busqueda; R2 autocompletado; R3 rangos; R6 ranking | Indices de estaciones; tabla hash compartida; pruebas y decisiones propias |
| Alejandro Curtidor | R5 viajes; R7 rutas; R8 cierres; R9 historial | Clase Red y carga; integracion del motor; pruebas y decisiones propias |

Todos aportan pruebas, mediciones y justificaciones R12 de su parte. Daniel
ensambla el panel; no tiene que descubrir ni escribir las decisiones de todos.
Todos deben poder explicar un requisito ajeno para la sustentacion.

## Aportes comprobados al preparar estas guias

- Catalina: configuracion de archivos ignorados (`e70a636`), base React y Vite
  (`8d6145b`), servidor Flask y conexion web (`44c5e03`).
- Daniel: pendientes de registrar.
- Mariana: pendientes de registrar.
- Alejandro: pendientes de registrar.

## Registro posterior

Cada persona agregara aqui una referencia a sus PR integradas y que hizo.
Como este archivo es compartido, se cambia en una PR corta independiente,
despues de actualizar la rama con `main`. No se inventan aportes ni se cambia
la identidad de Git para simular que trabajo otra persona.

El reparto se revisara tras la primera ronda: Alejandro concentra las
dependencias del motor y Catalina asume tambien datos e integracion. Si una
parte crece, se reasigna una tarea concreta y su archivo antes de empezarla.
