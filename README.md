# Planeador de viajes TransMilenio

Proyecto de Estructuras de Datos y Algoritmos de Catalina Vega, Mariana Parra,
Alejandro Curtidor y Daniel Rincon.

## Empieza aqui

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

## Ejecutar la base actual

Primero sigue [la instalacion](docs/INSTALACION.md). En la carpeta principal
del repositorio, abre dos terminales Command Prompt:

```cmd
.\.venv\Scripts\python.exe servidor.py
```

```cmd
npm --prefix frontend run dev
```

Abre la direccion Local que indique Vite. Actualmente se usan dos comandos.
Daniel implementara y documentara el comando unico de arranque exigido para
la entrega; todavia no existe.

## Decisiones del curso R12

Cada integrante escribira sus decisiones en `docs/decisiones/` usando
[la plantilla](docs/decisiones/PLANTILLA.md). Aqui se enlazaran las decisiones
terminadas de R1 a R10. No se presentan propuestas como decisiones ya probadas.

Todo el proyecto se desarrolla localmente. No requiere cuentas de IA, claves
de API, alojamiento ni servicios de pago para funcionar.
