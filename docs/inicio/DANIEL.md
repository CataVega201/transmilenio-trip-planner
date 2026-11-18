# Daniel Rincon

Empieza por [Instalación](INSTALACION.md) y pega el [prompt de preparación](TRABAJO_CON_IA.md). Para tu primera tarea usa la rama `daniel/r10-fila`.

**Tus archivos.** motor/fila.py, tests/test_fila.py, docs/decisiones/R10.md, componentes operacion/, simulacion/ y rendimiento/ bajo frontend/src/components/, rendimiento/, tests/integracion/ e iniciar.py.

**Prompts de implementación.** Pega uno a la vez junto con el prompt «Implementar». Para bloques que abarcan varios requisitos, entrega una tarea y una PR por vez. Comprueba primero qué está integrado en main.

### Bloque 1

> Implementa R10 como función suelta simular_fila(llegadas, frecuencia, capacidad). Usa FIFO propia y avanza entre eventos. Prueba llegadas simultáneas, cupo agotado, huecos largos y cientos de miles de pasajeros. Documenta tiempo, espacio y resultado.

### Bloque 2

> Implementa las pantallas Operacion y Simulacion con estilos locales, una por rama. Usa frontend/src/api.js según el contrato. Llama a onCambio tras una operación exitosa. Incluye estados de carga, vacío, error y éxito. Coordina con Catalina el montaje en App.

### Bloque 3

> Implementa R11 con mediciones reales n y 2n, medianas, variables y explicación de diferencias. Pide escenarios a cada autor. Integra pruebas de cierres/ediciones/deshacer y el arranque único iniciar.py --datos datos, usando crear_app y frontend/dist. Verifica en una copia nueva.

Al terminar cada tarea, usa el [prompt para subir y revisar](TRABAJO_CON_IA.md). Pide una explicación de un requisito ajeno para preparar la sustentación. Consulta tu [guía técnica ampliada](../miembros/DANIEL.md) y los [formatos exactos acordados](../CONTRATOS.md).
