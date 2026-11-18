# Instalacion desde cero en Windows

Haz una seccion a la vez. Catalina ya completo la instalacion y no debe clonar
otra copia ni recrear su entorno. Cada companero repite estos pasos en su PC.

## 1. Cuenta y acceso

1. Crea o abre tu propia cuenta en [GitHub](https://github.com/).
2. Acepta la invitacion de Catalina al repositorio
   `CataVega201/transmilenio-trip-planner`. Trabajamos como colaboradores del
   mismo repositorio; no necesitas pulsar **Fork**.
3. En tu foto de perfil, **Settings > Emails**, verifica tu correo. Guarda cual
   usaras; no uses el de Catalina ni el de otro integrante.
4. Si Catalina aun no tiene tu usuario, enviaselo para que te invite.

## 2. Programas

Instala solamente desde las paginas oficiales si aun no los tienes:

- [Visual Studio Code](https://code.visualstudio.com/).
- [Git para Windows](https://git-scm.com/downloads/win).
- [Python](https://www.python.org/downloads/). La base se comprobo con Python
  3.14.7. En el instalador activa **Add python.exe to PATH** cuando aparezca.
- [Node.js](https://nodejs.org/). La base se comprobo con Node 24.20.0 y npm
  11.19.0. Usa la misma version mayor 24; no reinstales si ya la tienes.

No necesitas instalar Java, React o Vite globalmente. React y Vite se descargan
con las dependencias del proyecto. No necesitas Codespaces, Docker, una cuenta
de alojamiento ni extensiones de IA.

Cierra y vuelve a abrir VS Code despues de instalar para que reconozca los
programas. Si tu Python tiene otra version y falla una dependencia, comparte
el error antes de cambiar archivos de versiones del grupo.

## 3. Elegir terminal y verificar

1. Abre VS Code. Pulsa **Ctrl + Shift + P**.
2. Escribe **Terminal: Select Default Profile** y selecciona **Command Prompt**.
3. Abre **Terminal > New Terminal**. El prompt debe parecerse a
   `C:\Users\TuUsuario>`. Si empieza con `PS`, abriste PowerShell; elige
   Command Prompt en la flecha al lado de **+** en el panel de terminal.
4. Ejecuta cada comando por separado, sin copiar el prompt:

```cmd
python --version
```

```cmd
python -m pip --version
```

```cmd
git --version
```

```cmd
node --version
```

```cmd
npm --version
```

Todos deben mostrar una version. Si dice `not recognized`, detente y revisa la
instalacion; no pegues comandos de reparacion encontrados al azar. Si `python`
abre Microsoft Store, comprueba `py --version` y pide ayuda para ajustar la ruta.

## 4. Identidad de Git

La identidad es local a tu PC, no inicia sesion en GitHub. Reemplaza los dos
textos dentro de comillas con TU nombre y TU correo verificado antes de ejecutar:

```cmd
git config --global user.name "TU NOMBRE REAL"
```

```cmd
git config --global user.email "TU CORREO VERIFICADO EN GITHUB"
```

Comprueba:

```cmd
git config --get user.name
```

```cmd
git config --get user.email
```

Si trabajas en un PC compartido, pide ayuda antes: en ese caso conviene configurar
la identidad solo en el repositorio y no globalmente. No compartan credenciales.

## 5. Descargar y abrir el repositorio una sola vez

1. En Command Prompt ejecuta:

```cmd
cd /d "%USERPROFILE%\Downloads"
```

```cmd
git clone https://github.com/CataVega201/transmilenio-trip-planner.git
```

```cmd
cd transmilenio-trip-planner
```

```cmd
code .
```

2. En la ventana nueva acepta **Yes, I trust the authors** si pregunta confianza.
3. Confirma en **Explorer**, icono de archivos de la izquierda, que ves
   `README.md`, `servidor.py`, `requirements.txt` y `frontend`.
4. Abre **Terminal > New Terminal** en ESA ventana. La ruta debe terminar en
   `transmilenio-trip-planner`. Todos los comandos siguientes parten de ahi.

Si ya existe una carpeta con ese nombre, no borres nada ni vuelvas a clonar
encima. Abre la copia existente y usa `git status` para identificarla.

## 6. Entorno de Python

Ejecuta uno por uno:

```cmd
python -m venv .venv
```

```cmd
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

```cmd
.\.venv\Scripts\python.exe --version
```

No hace falta activar el entorno ni cambiar politicas de PowerShell: usamos
la ruta explicita a Python. Si VS Code lo activa y aparece `(.venv)`, tambien
esta bien. No vuelvas a generar `requirements.txt` como parte de la instalacion.

En **Extensions**, icono de bloques a la izquierda, busca la extension **Python**
de **Microsoft** e instalala si falta. Despues **Ctrl + Shift + P > Python: Select
Interpreter** y elige `.venv\Scripts\python.exe`. Si no aparece, usa **Enter
interpreter path > Find** y selecciona ese archivo en tu copia local.

## 7. Dependencias de la pagina

Desde la carpeta principal ejecuta:

```cmd
npm --prefix frontend ci
```

Se usa `ci` porque ya existe `frontend/package-lock.json` y queremos reproducir
las versiones del grupo. No ejecutes `npm create vite` otra vez. Si `ci` dice
que el archivo de versiones no coincide, informa el error; no lo borres.

## 8. Comprobacion completa

En una terminal ejecuta y dejala abierta:

```cmd
.\.venv\Scripts\python.exe servidor.py
```

Debe indicar `Running on http://127.0.0.1:5000`. Abre
[la comprobacion de Flask](http://127.0.0.1:5000/api/estado): debe devolver
`estado: ok`. El aviso de servidor de desarrollo es normal durante esta etapa.

Abre otra terminal con **Terminal > New Terminal** y ejecuta:

```cmd
npm --prefix frontend run dev
```

Abre la direccion **Local** que muestre Vite, habitualmente
[http://localhost:5173/](http://localhost:5173/). Si ese puerto esta ocupado,
puede usar otro: abre el que indique la terminal. Debes ver
`Conexion con Python funcionando` (con la tilde correspondiente en la pagina).

En una tercera terminal verifica:

```cmd
npm --prefix frontend run build
```

```cmd
git status
```

La compilacion debe terminar sin errores y la instalacion no debe cambiar
archivos versionados. `.venv/`, `node_modules/` y `dist/` no se suben.
Para detener un servidor, haz clic en su terminal y pulsa **Ctrl + C**; si
Command Prompt pregunta `Terminate batch job (Y/N)?`, escribe **Y** y Enter.

## 9. Mensajes frecuentes

| Mensaje | Que hacer |
| --- | --- |
| `LF will be replaced by CRLF` | Aviso de saltos de linea en Windows; no impide el commit |
| Python Debugger quiere `Relaunch Terminal` | Es opcional para esta prueba; no reinicies una terminal que sirve la pagina sin necesidad |
| `Waiting for second key of chord` | Pulsa Esc y usa el menu o el icono; no todos los atajos coinciden |
| `running scripts is disabled` o error de PSReadLine | Usa Command Prompt y la ruta explicita a Python |
| `Address already in use` | Busca la terminal de Flask que ya esta abierta; no abras otro servidor en el mismo puerto |
| Pagina abierta, pero sin conexion | Comprueba Flask y `/api/estado`; despues revisa que Vite este abierto y recarga |
| Error de permisos al subir a GitHub | Comprueba que aceptaste la invitacion y que iniciaste sesion con tu propia cuenta |

No copies la carpeta `.venv` ni `node_modules` de otro computador. Cada PC las
genera con estos pasos. Tras la instalacion pasa a [Git paso a paso](GIT_PASO_A_PASO.md).
