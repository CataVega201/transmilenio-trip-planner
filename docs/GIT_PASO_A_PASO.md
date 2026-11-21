# Git y GitHub paso a paso

Usamos la terminal **Command Prompt** de VS Code, siempre en la carpeta principal
del repositorio. Ejecuta un comando a la vez y lee el resultado. Los comandos
de ejemplo sirven para una tarea de Catalina; en tu guia personal esta el nombre
de tu primera rama. No copies una rama de otra persona.

## 1. Palabras que vas a ver

| Palabra | Significado practico |
| --- | --- |
| Repositorio | Carpeta del proyecto y su historial |
| `main` | Version del grupo que debe mantenerse utilizable |
| Rama o branch | Linea de trabajo aislada para una tarea |
| Stage | Elegir los archivos que entraran en el proximo commit |
| Commit | Guardado local con autor y explicacion |
| Push | Subir tus commits a GitHub |
| Pull | Traer e integrar cambios del repositorio remoto |
| PR o Pull request | Solicitud para revisar e integrar una rama |
| Merge | Unir dos historiales, conservando sus commits |
| Conflicto | Git necesita que alguien decida como combinar cambios |

Guardar con **Ctrl + S** no crea un commit. Hacer commit no sube nada. Hacer push
a tu rama no integra nada en `main`. Abrir una PR tampoco la integra.

## 2. Antes de comenzar una tarea nueva

Primero abre una **Issue** en GitHub: **Issues > New issue**, escribe responsable,
archivos, resultado y pruebas, y pulsa **Create**. Comprueba que no exista ya.
Asigna tu usuario en **Assignees**. No es necesario usar un proyecto o una app extra.

En VS Code ejecuta:

```cmd
git status
```

Si dice `working tree clean`, puedes seguir. Si hay cambios, primero termina y
guarda los de tu tarea actual siguiendo la seccion 4. No cambies de rama con
cambios sin guardar en Git y no uses **Discard Changes** para limpiar.

```cmd
git switch main
```

```cmd
git pull --ff-only origin main
```

Si informa divergencia o falla, detente y ve a la seccion de problemas. Si termina
bien, crea una rama nueva. Ejemplo para la primera tarea de Catalina:

```cmd
git switch -c catalina/r4-horarios
```

Usa el nombre de TU guia. Para tareas siguientes, elige un nombre nuevo y corto,
como `daniel/panel-r11`; no reutilices una rama ya integrada.

```cmd
git branch --show-current
```

Debe mostrar tu rama. Si muestra `main`, no empieces a editar. Comenta en la Issue
el nombre de la rama y los archivos que vas a tocar.

## 3. Mientras trabajas

- Edita solo los archivos de la tarea y guarda con **Ctrl + S**.
- Mira **Source Control**, icono de ramificacion en la barra izquierda, para ver
  los cambios. Pulsa un archivo para comparar sus versiones.
- No pulses **Sync Changes** durante el trabajo en equipo: aqui usaremos los
  comandos explicitos para distinguir actualizar, subir e integrar.
- No cambies versiones, archivos de contratos ni estilos globales para resolver
  un problema local sin acordarlo con su responsable.
- Si necesitas pausar, sube un avance que puedas describir de forma honesta y
  deja una PR **Draft**. Un commit incompleto debe decir que esta incompleto;
  no se integra en `main`.

## 4. Guardar y subir una tarea

Prueba tu parte con las instrucciones de tu guia. Despues:

```cmd
git status
```

```cmd
git diff
```

`git diff` compara archivos ya versionados; los nuevos se revisan abriendolos
en Explorer. Si Git abre un visor y no puedes escribir comandos, pulsa **q**
para salir.

Prepara solo tus archivos. Ejemplo de R4; debe hacerse despues de crearlos:

```cmd
git add motor/horarios.py tests/test_horarios.py docs/decisiones/R4.md
```

No uses `git add .`: podrias incluir cambios ajenos o archivos no previstos.
Si una ruta no existe, Git lo dira; revisa que archivo creaste antes de continuar.

```cmd
git diff --cached --stat
```

Comprueba la lista y revisa el contenido preparado:

```cmd
git diff --cached
```

```cmd
git commit -m "Implementa busqueda del proximo bus y casos extremos"
```

El mensaje debe describir TU cambio. La primera vez que subes una rama, ejemplo:

```cmd
git push -u origin catalina/r4-horarios
```

Para los siguientes commits de esa misma rama basta:

```cmd
git push
```

Si pide autenticacion, completa el inicio de sesion del navegador con tu cuenta.
No pongas contrasenas ni tokens en archivos, terminales compartidas o mensajes.
No uses `git push origin main` para entregar una tarea.

## 5. Abrir una Pull request

1. Abre el repositorio en GitHub.
2. Si aparece **Compare & pull request**, pulsalo. Si no: **Pull requests > New
   pull request**.
3. Verifica **base: main** y **compare: tu rama**. Una base equivocada puede
   mezclar trabajos que no corresponden.
4. Pon un titulo concreto. Completa la plantilla con lo que cambia, como se
   comprobo, decisiones y pendientes. Enlaza la Issue escribiendo `Closes #`
   seguido del numero real; por ejemplo `Closes #12` solo si tu Issue es la 12.
5. Si no esta terminada, usa la flecha junto a **Create pull request** y elige
   **Create draft pull request**. Si esta lista, crea la PR normal.
6. En **Reviewers** elige a otro integrante. Si no te deja, deja un comentario
   solicitando revision; no inventes usuarios ni menciones personas ajenas.

Las correcciones se hacen en la misma rama con nuevos commits y `git push`.
GitHub actualiza la PR automaticamente. No abras otra PR para la misma tarea.

## 6. Incorporar lo que ya integro el grupo

Hazlo cuando otra PR se integro mientras trabajabas y antes de la revision final.
Primero confirma que estas en tu rama y que todo esta guardado mediante commits:

```cmd
git branch --show-current
```

```cmd
git status
```

Solo si indica `working tree clean`:

```cmd
git fetch origin
```

```cmd
git merge --no-edit origin/main
```

Si no hay conflictos, repite tus pruebas y sube el resultado con `git push`.
Si hay conflictos, sigue la seccion 9. No uses rebase, force push ni reset para
silenciarlos. Antes de integrar una PR, revisar de nuevo si `main` avanzo.

## 7. Revisar e integrar

El revisor abre **Files changed**, lee los cambios y comprueba:

- Los archivos y firmas coinciden con la tarea y los contratos.
- Se entienden el algoritmo y los casos extremos; el motor no usa prohibiciones.
- El autor adjunto resultados de pruebas y ejecuto la parte afectada.
- Los metodos publicos funcionan juntos y no solo por separado.

Si quiere probar la rama en su equipo, primero su trabajo debe estar guardado
y subido y `git status` debe estar limpio. Ejecuta `git fetch origin`. Si nunca
ha descargado esa rama, usa por ejemplo:

```cmd
git switch --track origin/catalina/r4-horarios
```

Si ya tiene esa rama local, usa `git switch catalina/r4-horarios` y despues
`git pull --ff-only`. No edita ni hace commits en la rama del autor. Despues
regresa a su propia rama con `git switch` y su nombre. Si no existe el nombre
o el cambio falla, detente en lugar de crear una rama de prueba equivocada.

En GitHub el revisor pulsa **Review changes**, elige **Approve** o **Request
changes** y **Submit review**. Aprobar no es implementar el requisito por otro.
El autor atiende comentarios y explica las decisiones.

Con revision aprobada, pruebas correctas y base actualizada, el autor o Catalina
usa **Create a merge commit > Confirm merge**. Si el boton muestra otro metodo,
abre su flecha y selecciona **Create a merge commit**. Si no esta disponible,
Catalina revisa la configuracion; no se cambia a squash por comodidad.

No se integra una PR **Draft**, con conflictos, sin pruebas o cambiando contratos
sin acuerdo. No se exige que un revisor concreto este conectado: cualquier otro
integrante puede revisar. Si todos estan ausentes, se deja pendiente y se avanza
en una tarea independiente.

## 8. Despues de integrar y al retomar trabajo

Con tu trabajo guardado y sin cambios pendientes:

```cmd
git switch main
```

```cmd
git pull --ff-only origin main
```

Comprueba que ves el cambio integrado. Crea otra rama para tu tarea siguiente;
no vuelvas a programar sobre la rama anterior ni sobre `main`. Si una dependencia
cambio, repite la instalacion correspondiente: `npm --prefix frontend ci` cuando
cambie el archivo de versiones, o `python` del entorno con `-m pip install -r
requirements.txt` cuando cambien las dependencias de Python.

Si retomas una tarea sin integrar, cambia a SU rama, comprueba su estado,
trae sus cambios remotos con `git pull --ff-only` si esta limpio y sigue la
seccion 6. No crees otra rama con el mismo trabajo.

## 9. Que hacer ante un conflicto

Un conflicto no significa que perdiste archivos. No pulses automaticamente
**Accept Current**, **Accept Incoming** ni **Accept Both**: esas opciones pueden
dejar una version que compila pero borra comportamiento necesario.

Si el conflicto aparecio en el `git merge --no-edit origin/main` de la seccion 6,
y el estado estaba limpio antes de empezarlo:

```cmd
git status
```

Copia la lista de archivos en conflicto para pedir ayuda al otro autor. Si no
sabes resolverlo, cancela ESE merge:

```cmd
git merge --abort
```

Tus commits previos se conservan. Este comando no aplica a errores de instalacion,
ni debe ejecutarse si no hay un merge en curso. Despues escribe en la PR que
archivos chocaron y cual es el mensaje. Pueden continuar tareas independientes.

Para resolverlo con el otro autor, vuelve a ejecutar el merge con estado limpio,
abre los archivos y compara ambas intenciones. Eliminen los marcadores
`<<<<<<<`, `=======`, `>>>>>>>` conservando la logica necesaria. Prepara solamente
los archivos resueltos, ejecuta las pruebas, y termina con:

```cmd
git commit -m "Integra cambios de main y resuelve compatibilidad"
```

```cmd
git push
```

Si no puedes explicar la combinacion, no la confirmes. Incluye al responsable
del archivo y deja la PR sin integrar hasta resolverlo.

## 10. Otros problemas frecuentes

| Situacion | Accion |
| --- | --- |
| Edite en `main` pero aun no hice commit | Crea una rama nueva con `git switch -c` y un nombre propio antes de preparar el commit; los cambios pasan a esa rama |
| Hice commit en `main` sin subir | Detente y pide ayuda mostrando `git status` y `git log -3 --oneline`; no hagas push ni reset |
| Prepare un archivo equivocado | `git restore --staged` seguido de la ruta exacta lo saca del proximo commit y conserva su contenido local |
| `nothing to commit` | Revisa que guardaste el editor, estas en la carpeta correcta y no hiciste ya ese commit |
| `non-fast-forward` o historias divergentes | No uses `--force`. Revisa rama y `git status`; pide ayuda si alguien mas escribio en tu rama |
| `branch already exists` | Puede ser una tarea anterior; no la borres. Revisa las ramas y elige el nombre correcto |
| Muchas dependencias aparecen para subir | Detente; revisa `.gitignore`. No subas `.venv`, `node_modules` ni `dist` |
| Archivos con cambios que no reconozco | No los borres ni los prepares. Consulta su origen antes de continuar |

No usar `git reset --hard`, `git clean`, `git push --force`, borrar `.git` ni
descartar cambios como solucion generica. Ante dudas, conservar el trabajo y
compartir el mensaje exacto es mejor que probar comandos destructivos.

## 11. Configuracion de proteccion pendiente

Catalina puede configurar despues en GitHub **Settings > Branches > Add classic
branch protection rule**, patron `main`: **Require a pull request before merging**,
una aprobacion y **Require conversation resolution before merging**. Incluir a
administradores mediante **Do not allow bypassing the above settings** si aparece;
no habilitar force push ni borrado de `main`.

No marcar comprobaciones automaticas como obligatorias hasta que existan y
funcionen. Estas guias no crean CI ni activan protecciones. Al usar una revision
obligatoria se podra programar a solas, pero integrar requerira respuesta de otro.

Referencia: [proteccion de ramas en GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
