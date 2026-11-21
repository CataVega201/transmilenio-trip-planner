# Alejandro Curtidor

Empieza por [Instalación](INSTALACION.md) y pega el [prompt de preparación](TRABAJO_CON_IA.md). Para tu primera tarea usa la rama `alejandro/r7-rutas`.

**Tus archivos.** motor/rutas.py, viajes.py, historial.py, carga.py, red.py y __init__.py dentro de motor/. Pruebas test_rutas.py, test_viajes.py, test_historial.py y test_red.py en tests/. Decisiones R5, R7, R8 y R9.

**Prompts de implementación.** Pega uno a la vez junto con el prompt «Implementar». Para bloques que abarcan varios requisitos, entrega una tarea y una PR por vez. Comprueba primero qué está integrado en main.

### Bloque 1

> Implementa R7 en motor/rutas.py con recorridos en ambos sentidos e inserción y eliminación de paradas. Prueba cabeza, cola y ruta vacía. Documenta tanto el costo de localizar una parada como el de editarla. Deja el acceso por nombre preparado para TablaHash de Mariana.

### Bloque 2

> Implementa R9 y R8. Registra solo cambios exitosos. Un cambio nuevo vacía rehacer. Deshacer y rehacer restauran recorrido, estado e índices. Coordina con Mariana cambiar_estado y la actualización del ranking; prueba secuencias combinadas.

### Bloque 3

> Implementa la carga de los tres CSV y Red(carpeta), delegando R1–R4 y R6. Implementa R5 con cero o un transbordo y el menor número de paradas. Respeta el sentido y los cierres. Exporta Red y simular_fila cuando sus módulos existan. Prueba otra red y documenta R5, R7, R8 y R9.

Al terminar cada tarea, usa el [prompt para subir y revisar](TRABAJO_CON_IA.md). Pide una explicación de un requisito ajeno para preparar la sustentación. Consulta tu [guía técnica ampliada](../miembros/ALEJANDRO.md) y los [formatos exactos acordados](../CONTRATOS.md).
