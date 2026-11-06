# Base visual compartida

Responsable de integracion: Catalina. Esta rama entrega tema y pantalla inicial;
los controles de consultas, viajes, operacion y rendimiento siguen pendientes.

## Reglas para los componentes de Daniel y Catalina

- Reutilizar las variables de `frontend/src/styles/tema.css`, importadas desde
  index.css. No copiar colores distintos a cada pantalla.
- Color principal: rojo oscuro `--color-marca`. Texto normal: `--color-texto`;
  texto secundario: `--color-secundario`. Fondos y bordes tienen variables propias.
- Usar la fuente del sistema: no hay descargas de fuentes ni servicios externos.
- Usar espacios de la escala `--espacio-*` y `--radio` para tarjetas.
- CSS de cada pantalla junto a su componente, con sus prefijos acordados:
  consulta-, viaje-, operacion-, fila- y rendimiento-. El prefijo app- pertenece
  a la estructura general. No editar App.css ni tema.css al mismo tiempo que
  Catalina: proponer el cambio en la Issue y coordinarlo.
- Disposicion principal de una columna por debajo de 800 px; formularios y
  resultados deben caber a 320 px y con zoom de 200 %. No usar anchos fijos
  grandes para campos. Las tablas extensas necesitan su propio desplazamiento.
- Etiquetas visibles para campos, foco de teclado visible y estados expresados
  con texto ademas de color. Objetivo de contraste: 4.5:1 para texto normal.
- Botones para acciones, enlaces para navegacion. No poner tarjetas clicables
  ni botones que aparenten funciones todavia inexistentes.
- Mostrar carga, vacio, error y resultado. No afirmar disponibilidad de un
  viaje ni exito de una operacion antes de recibir la respuesta del motor.

## Pantalla inicial actual

La ilustracion es decorativa, hecha con CSS y oculta a lectores de pantalla.
No representa el mapa real. Las tres tarjetas describen funciones en preparacion.
El enlace principal lleva a esa seccion. Se conserva la comprobacion real de
conexion con Flask y se identifica el caracter academico del proyecto.

## Comprobacion manual antes de integrar

1. Abrir la pagina con Vite y Flask activos; comprobar conexion y anclas.
2. Recorrer con Tab: enlace para saltar al contenido, marca y enlace de seccion.
3. Revisar a 320 px, en escritorio y con zoom de 200 %: no debe cortarse texto
   ni aparecer desplazamiento horizontal de toda la pagina.
4. Ejecutar `npm --prefix frontend run build` y adjuntar una captura a la PR.

La compilacion por si sola no acredita estas comprobaciones visuales.
