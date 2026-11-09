# Guia general del equipo

Esta guia permite trabajar a distintas horas sobre el mismo proyecto. Primero
se prepara el equipo; despues cada persona trabaja en sus archivos, prueba su
parte y la entrega mediante una solicitud de revision en GitHub. No hay que
esperar a que todos esten conectados para programar.

## 1. Estado del trabajo al 8 de noviembre

Los avances siguientes están en ramas de revisión. Se vuelven accesibles desde main cuando otro integrante revisa y el equipo integra la PR correspondiente.

| Avance | Dónde revisarlo | Pendiente |
| --- | --- | --- |
| Base local, React, Flask y conexión | main | Comando único a cargo de Daniel |
| Guías individuales y acuerdos | docs/guias-equipo | Revisión del equipo |
| Tema y pantalla adaptable | catalina/tema-web | Revisión visual del equipo |
| Índice R4 y decisiones | [PR #3](https://github.com/CataVega201/transmilenio-trip-planner/pull/3) | Probar con TablaHash de Mariana y Red de Alejandro |
| Conversión real y CSV | [PR #4](https://github.com/CataVega201/transmilenio-trip-planner/pull/4) | Revisar el alcance troncal y la regla de plataformas |
| Consultas, viajes y adaptador Flask | [PR #6](https://github.com/CataVega201/transmilenio-trip-planner/pull/6) | Integrar con los módulos reales y componentes de Daniel |
| R1–R3, R5–R9, R10 y panel R11 | Guías de Mariana, Alejandro y Daniel | Implementación por sus responsables |

La conversión incluye datos/ con los CSV del profesor y datos_generados/ con la salida del GTFS real. La PR #6 tiene como base la rama del tema visual. Primero se integra el tema en main y después se comprueba que la PR #6 tenga main como base antes de integrarla.

## 2. Orden para una persona que empieza

1. Acepta la invitacion al repositorio con tu propia cuenta de GitHub.
2. Sigue [INSTALACION.md](INSTALACION.md). Catalina ya tiene la base instalada.
3. Lee [GIT_PASO_A_PASO.md](GIT_PASO_A_PASO.md).
4. Lee [CONTRATOS.md](CONTRATOS.md) y tu guia personal.
5. Trabaja solamente en tu primera tarea; no ejecutes todos los pasos del
   proyecto el primer dia.

Las instrucciones de instalacion son para Windows y terminal Command Prompt,
con los menus de VS Code y GitHub en ingles. Cada persona usa su propia carpeta
local. No se comparte una carpeta por OneDrive ni se trabaja en el equipo ajeno.

## 3. Como se conectan las partes

```text
Persona en el navegador
        |
        v
React en frontend/  ---> peticion /api/... ---> Flask en servidor.py
                                                   |
                                                   v
                                             motor.Red
                                                   |
                                                   v
                                      tres CSV en una carpeta elegida
```

React recoge entradas y muestra resultados. Flask valida la forma de las
peticiones y convierte respuestas a JSON. El motor decide si una estacion esta
cerrada, como buscar, que viaje sirve y como deshacer. Nunca se arregla una regla
del motor solamente ocultando un boton en React.

Para ejecutar el motor, el profesor debe poder hacer `from motor import Red,
simular_fila` sin instalar Flask, sin arrancar servidores y sin importar React.
Importar el paquete tampoco debe leer automaticamente una red fija.

## 4. Reparto de archivos

Las rutas marcadas como previstas se crearan en sus tareas. No existen todavia
solo porque aparezcan en esta tabla.

| Responsable | Archivos propios previstos |
| --- | --- |
| Catalina | `motor/horarios.py`, `tests/test_horarios.py`, `frontend/src/components/consultas/`, `frontend/src/components/viajes/`, `frontend/src/styles/tema.css`, `conversion/`, `docs/decisiones/R4.md` |
| Daniel | `motor/fila.py`, `tests/test_fila.py`, `frontend/src/components/operacion/`, `frontend/src/components/simulacion/`, `frontend/src/components/rendimiento/`, `rendimiento/`, `tests/integracion/`, `iniciar.py`, `docs/decisiones/R10.md` |
| Mariana | `motor/tabla_hash.py`, `motor/estaciones.py`, `motor/indice_alfabetico.py`, `motor/ranking.py`, `tests/test_tabla_hash.py`, `tests/test_estaciones.py`, `tests/test_ranking.py`, decisiones R1 R2 R3 R6 |
| Alejandro | `motor/__init__.py`, `motor/red.py`, `motor/carga.py`, `motor/rutas.py`, `motor/viajes.py`, `motor/historial.py`, `tests/test_red.py`, `tests/test_rutas.py`, `tests/test_viajes.py`, `tests/test_historial.py`, decisiones R5 R7 R8 R9 |

| Archivos compartidos | Quien integra los cambios |
| --- | --- |
| `servidor.py`, `frontend/src/api.js`, `frontend/src/App.jsx`, `frontend/src/App.css`, `frontend/src/index.css`, `frontend/src/main.jsx`, `frontend/index.html`, `frontend/vite.config.js` | Catalina |
| `frontend/package.json`, `frontend/package-lock.json`, `requirements.txt`, `.gitignore` | Catalina; dependencias y su archivo de versiones juntos en la misma PR |
| `docs/CONTRATOS.md`, `docs/GUIA_GENERAL.md`, `README.md` | Catalina tras acuerdo escrito en una Issue |
| `datos/estaciones.csv`, `datos/rutas.csv`, `datos/horarios.csv` | Catalina mediante el conversor; no editar a mano |
| `integrantes.md` | Cada autor en PR corta, sin dos PR simultaneas sobre el archivo |
| `.github/` | Daniel cuando se implemente automatizacion; Catalina integra esta base documental |

Responsable significa quien hace la edicion normalmente. No es una prohibicion
permanente: para ayudar en otro archivo, primero se acuerda la cesion en su Issue.
Los estilos de cada componente se guardan junto al componente y usan un prefijo
propio: `consulta-`, `viaje-`, `operacion-`, `fila-`, `rendimiento-`. Evitar reglas
generales como `button { ... }` en estilos individuales: pueden alterar pantallas
ajenas sin que Git detecte un conflicto.

## 5. Trabajo asincrono sin pisarse

1. Cada tarea se registra en **Issues** de GitHub. El titulo empieza por el
   requisito, por ejemplo `R4 - Buscar el siguiente horario`.
2. La descripcion indica responsable, archivos, resultado esperado,
   dependencia y pruebas. La persona se asigna con **Assignees** y comenta
   `Inicio esta tarea en catalina/r4-horarios`. Antes comprueba que nadie la
   haya reclamado. Una tarea tiene un responsable; no dos ramas competidoras.
3. Cada tarea tiene una rama nueva creada desde `main` actualizado. No se
   mantienen cuatro ramas eternas, ni todos trabajan en la misma rama.
4. Se guardan avances reales mediante commits y se suben a la rama propia al
   terminar cada sesion. Una PR en **Draft** permite dejar contexto sin pedir
   todavia la integracion.
5. Antes de pasar a **Ready for review**, se incorpora el `main` actual y se
   repiten las comprobaciones relevantes. El autor no cambia contratos ajenos
   para hacer pasar una prueba local.
6. Otro integrante revisa. Si el revisor habitual esta ausente, puede hacerlo
   cualquiera de los otros dos. Mientras tanto el autor puede empezar otra tarea
   independiente desde `main`, manteniendo la anterior subida y sin cambios
   locales pendientes. No se arranca una tarea que dependa de una PR sin integrar.
7. Tras aprobar, el autor o Catalina integra con **Create a merge commit**.
   Se conserva el historial de commits individuales; no usar **Squash and merge**
   para este proyecto. No integrar dos PR al mismo tiempo: quien haga la segunda
   comprueba de nuevo su base y las pruebas con el `main` actualizado.
8. Tras integrar se puede borrar la rama remota con **Delete branch**. El historial
   en `main` permanece. Los demas actualizan al empezar su siguiente sesion.

Rotacion sugerida de revision: Daniel revisa a Catalina; Mariana a Daniel;
Alejandro a Mariana; Catalina a Alejandro. La revision incluye que el autor
explique el algoritmo, no solo que la pagina se vea bien.

Nadie tiene que estar conectado a la vez para editar. La revision final puede
esperar; el trabajo independiente puede continuar. No prometemos cero conflictos:
las ramas separan trabajo, pero los cambios incompatibles necesitan resolverse.

## 6. Acuerdos comunes antes de escribir codigo

[CONTRATOS.md](CONTRATOS.md) fija nuestra propuesta de respuestas, entradas,
errores, limites entre modulos y formatos web. El material del profesor no
especifica todos esos detalles. Son decisiones del grupo y podrian requerir
adaptacion si aparece un contrato oficial; no garantizan compatibilidad con un
calificador desconocido.

Antes de implementar, cada responsable deja en su Issue una confirmacion de que
leyo esos acuerdos o la propuesta concreta que quiere cambiar. Catalina integra
las modificaciones acordadas antes del codigo que depende de ellas. No se bloquea
el resto de tareas por una decision no relacionada.

No cambiar una firma publica, una respuesta JSON o el nombre de una propiedad
compartida en una PR de otro tema. Para cambiarlos: Issue con ejemplo anterior y
nuevo, personas afectadas, PR del contrato y luego PR de los consumidores.

## 7. Orden de construccion y dependencias

| Etapa | Catalina | Daniel | Mariana | Alejandro |
| --- | --- | --- | --- | --- |
| A, trabajo independiente | R4 con horarios pequenos en memoria | R10 con casos pequenos | Tabla hash e indices de estaciones | Lista de rutas e historial; define fachada Red sin sustituir codigo ajeno |
| B, modulos | Validacion de CSV y conversor cuando este disponible el GTFS | Estructura de mediciones; componentes de operacion con datos de ejemplo | R1 R2 R3 R6 y notificaciones de cambios | Carga CSV, integra modulos ya aceptados, R5 R7 R8 R9 |
| C, conexion real | Adaptador Flask, consultas y viajes | Conecta sus componentes usando `api.js`; ensambla R11 | Mide y corrige sus consultas | Prueba secuencias de cambios y viajes; mide sus operaciones |
| D, entrega | Diseno adaptable y conversion reproducible | Arranque unico y pruebas integrales | Rendimiento y decisiones propias | Rendimiento y decisiones propias |

En A no se espera al GTFS ni a Red para probar un algoritmo. Se usan entradas
pequenas en `tests/`, fuera de `motor/`. Las pantallas pueden usar ejemplos locales
en su carpeta, con la etiqueta visible `Datos de ejemplo`. No se agregan rutas
ficticias al servidor real ni se presentan ejemplos como red real.

Para integrar Red: primero tabla hash y rutas, despues estaciones/horarios/fila,
despues la carga y las consultas publicas, despues cierres e historial conectados,
y finalmente viajes completos y API. Alejandro puede entregar metodos por partes;
no debe crear una segunda implementacion de R1 a R4 para suplir dependencias.

## 8. Condiciones para dar una tarea por terminada

- Cumple el requisito y los casos extremos acordados.
- Tiene pruebas con red pequena y al menos un caso que fallaba antes o diferencia
  el algoritmo correcto de una solucion ingenua. No basta comprobar que importa.
- Dentro de `motor/` se respetan todas las prohibiciones del curso.
- Incluye su decision R12: estructura, algoritmo, alternativa, Big O y definicion
  de variables. Describe si el costo es esperado, amortizado o peor caso.
- Aporta mediciones cuando su operacion este lista. R5 tiene pruebas funcionales
  aunque no se evalua su crecimiento temporal.
- No rompe el arranque de la base existente ni cambia archivos ajenos sin acuerdo.
- La PR explica como verificar y tiene revision de otra persona.

No se pide una cantidad artificial de commits. Se registran cambios coherentes a
lo largo del desarrollo: algoritmo, casos extremos y correcciones. Todos usan
su identidad real, entienden lo que entregan y pueden explicarlo sin asistencia.

## 9. Rendimiento R11 y decisiones R12

Daniel prepara la infraestructura; cada autor aporta sus operaciones. Se mide
con redes sinteticas de tamanos crecientes, incluida una comparacion n y 2n.
Las mediciones de Python se hacen junto al motor, no cronometrando la red HTTP.
Los generadores y graficas van fuera de `motor/` y pueden usar herramientas
permitidas fuera del paquete.

Indicar que crece: estaciones, rutas, paradas por ruta, horarios o pasajeros.
Controlar tambien el tamano de salida y k. Una consulta de rango que devuelve
el doble de nombres tarda mas aunque el acceso al indice sea bueno. Usar
repeticiones, calentamiento y mediana; separar construccion, consultas y cambios.
Medir cache fria y caliente si existe; no esconder una reconstruccion costosa.
R7 debe incluir el costo de localizar la parada y mantener indices, no solo
el cambio de enlaces. Deshacer debe mantener todos los indices coherentes.

El panel debe cubrir carga y metodos publicos R1 a R10, incluidos cambios,
recorrido, deshacer y rehacer; R5 puede mostrarse como funcional, sin prometer
un objetivo de rendimiento del curso. Cualquier diferencia frente a la
complejidad esperada se explica en la misma vista con mediciones reales.

## 10. Costo y herramientas

La ejecucion prevista es local, sin servicios de pago ni claves de API. Se usan
Python, Flask, Node.js, React, Vite, Git, VS Code y el repositorio publico existente.
No se necesita una suscripcion de IA para desarrollar ni para ejecutar la app.
Las guias no dependen de cuotas gratuitas de Copilot o Codex. Si se usa asistencia,
el integrante revisa el codigo y mantiene su responsabilidad sobre lo entregado.

No se configura alojamiento ni se asegura disponibilidad gratuita de un servidor
publico. GitHub Pages por si solo no ejecuta nuestro motor Python. La entrega
actual prevista es el repositorio y ejecucion local con un comando al finalizar.

## 11. Antes de la entrega

- Clonar en una carpeta nueva y seguir el README sin pasos secretos.
- Instalar dependencias, generar datos con el conversor y ejecutar con un comando.
- Verificar el motor con una segunda red pequena que no use nombres de la real.
- Probar un cierre, una edicion, dos deshacer, dos rehacer y un cambio nuevo que
  vacie rehacer; comprobar consultas, viajes, ranking y horarios despues.
- Comprobar el panel con datos reales medidos y todas las decisiones R12 enlazadas.
- Verificar nombres y aportes reales en `integrantes.md`, acceso del profesor e
  historial de los cuatro. Los commits deben estar integrados en `main`.
- Rotar explicaciones: cada uno explica una parte que no implemento y todos
  ensayan un cambio pequeno sin depender de otra persona.

## Fuentes de colaboracion

El flujo se adapta de [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow).
La [proteccion de ramas](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
puede exigir PR y revision en repositorios publicos de GitHub Free. Estas guias
no activan configuraciones remotas: hasta configurarlas, son acuerdos manuales.
