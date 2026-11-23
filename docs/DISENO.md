# Diseño y accesibilidad de la interfaz

La interfaz conserva los colores de Bogotá y TransMilenio con una portada más
visual, un mapa ilustrativo en SVG y accesos directos a herramientas reales.
La ilustración es decorativa: no representa una ruta real ni datos en vivo.
No se descargan fuentes, imágenes ni librerías de animación externas.

## Navegación

- Cliente/Operador se selecciona en el menú de perfil de la esquina superior
  derecha. Es un selector de vistas, no autenticación; la demo es compartida.
- El menú usa details/summary nativos, botones con estado aria-pressed, Escape
  para cerrar y retorno del foco al selector al elegir una vista.
- Consultas y Viajes están disponibles en ambas vistas. Operador añade gestión,
  simulación y rendimiento, con navegación directa a cada sección.
- Los componentes permanecen montados: cambiar de vista conserva formularios
  y resultados. Los cierres siguen refrescando consultas mediante versionRed.

## Reglas compartidas

Usar las variables de frontend/src/styles/tema.css para colores, espacios,
controles y sombras. Los componentes conservan sus prefijos consulta-, viaje-,
operacion-, fila- y rendimiento-. App.css controla la estructura general.

- Campos con etiquetas visibles; ayudas y resultados expresados con texto.
- Foco visible, enlace para saltar al contenido y navegación con teclado.
- Contraste mínimo objetivo: 4.5:1 para texto normal y 3:1 para controles.
- Controles de acción de al menos 44 px de alto; etiquetas amplían las zonas
  de interacción de radios y casillas. Campos con texto de al menos 16 px.
- Formularios fluidos, sin impedir zoom ni desplazamiento. Las tablas extensas
  tienen su propio desplazamiento, nombre accesible y foco de teclado.
- Animaciones de entrada finitas, sin parpadeo ni movimiento continuo.
  prefers-reduced-motion desactiva animaciones y desplazamiento suave.
- El modo de contraste forzado conserva bordes, selección y foco.

## Verificación de esta actualización

- ESLint y compilación Vite correctos; cuatro pruebas de API aprobadas.
- Anchos 320, 390, 768, 1024 y 1440 px sin desbordamiento horizontal en la
  vista Operador; menú de perfil comprobado a 320 px.
- Enter/Tab para abrir y elegir, Escape para cerrar y retorno de foco.
- Consulta real de estación y ejemplo de simulación del profesor correctos.
  El resultado de simulación se conserva tras cambiar a Cliente y volver.

Estas comprobaciones no equivalen a una certificación WCAG ni cubren todas
las combinaciones de navegador, dispositivo y lector de pantalla. La revisión
con tecnologías de asistencia reales sigue siendo necesaria para certificarla.
