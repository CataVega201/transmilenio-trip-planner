# Integración de consultas y viajes

Catalina mantiene servidor.py, frontend/src/api.js y las pantallas Consultas y Viajes. Esta rama parte del tema visual de Catalina. Para integrar ambas PR en main, revisar primero el tema.

## Probar la rama en Windows

Desde la raíz del repositorio, arrancar Flask y Vite en terminales distintas según el README. Los formularios usan /api mediante el proxy de Vite. Flask responde con estado 503 mientras la función solicitada siga pendiente. La conexión con Python en el pie verifica la salud del servidor.

Comprobar el adaptador desde la raíz:

```cmd
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_api_catalina.py -v
npm --prefix frontend run lint
npm --prefix frontend run build
```

Las pruebas usan un motor de prueba para verificar el paso de argumentos y resultados. La prueba de integración con los algoritmos reales corresponde a la etapa en que se unan las ramas de los cuatro integrantes.

## Mariana y Alejandro

El servidor obtiene Red del paquete motor y llama a las firmas de la guía general. Construye una instancia por aplicación y comparte los cambios entre solicitudes. La carpeta por defecto es datos junto a servidor.py. Alejandro puede inyectar una Red de prueba con crear_app(red=instancia).

## Daniel

Los nombres de las funciones de frontend/src/api.js coinciden con el contrato. Devuelven una promesa con los datos o un error legible. Usa estas funciones desde tus componentes propios. Al integrar Operacion en App, Catalina conectará onCambio a un contador versionRed que Consultas y Viajes ya aceptan.

Para el arranque único, crear_app(carpeta_datos, carpeta_web) acepta la carpeta de los CSV y la ruta absoluta a frontend/dist después de compilar. Para el panel, pasa medir=funcion con firma (tamanos, repeticiones). Para la fila se carga motor.simular_fila o se puede inyectar simular=funcion en pruebas. Daniel conserva sus archivos de simulación, panel, operación y arranque.

