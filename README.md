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

React y Flask funcionan en main. El progreso de cada rama y las dependencias para integrar el motor se encuentran en la [guía general](docs/GUIA_GENERAL.md). Las pruebas del conversor ya incluyen el GTFS real de julio de 2021. Cada integrante debe revisar e integrar los cambios del equipo antes de usar esas funciones desde main.

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

Cada integrante escribira sus decisiones en `docs/decisiones/` usando
[la plantilla](docs/decisiones/PLANTILLA.md). Aqui se enlazaran las decisiones
terminadas de R1 a R10. No se presentan propuestas como decisiones ya probadas.

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
