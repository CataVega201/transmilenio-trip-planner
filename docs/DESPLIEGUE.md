# Despliegue público en Render

El servidor ejecuta Python y sirve el frontend compilado en el mismo dominio.
Waitress mantiene una instancia de la red en un proceso; las ediciones y el
historial permanecen en memoria hasta reiniciar o desplegar de nuevo.

1. Inicia sesión en https://dashboard.render.com y elige New > Blueprint.
2. Selecciona el repositorio público CataVega201/transmilenio-trip-planner,
   rama main. La configuración está en render.yaml y declara el plan free.
3. Confirma el servicio gratuito. Cuando Render indique Live, abre su enlace
   onrender.com y comprueba Consultas, Viajes, Operación, Simulación y Rendimiento.

Si creas un Web Service manual, usa Python, el plan Free, estos comandos y
la raíz del repositorio sin subcarpeta:

- Build: pip install -r requirements.txt && npm --prefix frontend ci && npm --prefix frontend run build
- Start: python produccion.py
- Health check: /api/estado
- PYTHON_VERSION=3.14.0 y NODE_VERSION=24.

Render aporta PORT. No se requieren claves de API ni credenciales en el código.
La primera visita puede tardar aproximadamente un minuto tras 15 minutos sin
actividad en el plan gratuito. Los cambios de red se pierden al reiniciar.
Una sola medición R11 se ejecuta a la vez; las demás reciben un aviso 429.

La URL definitiva debe registrarse en la sección App desplegada del README
una vez verificada públicamente. El despliegue está pendiente hasta tener esa URL.
