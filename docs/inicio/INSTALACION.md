# Instalación en Windows

**1. Prepara tu cuenta y tus programas.** Acepta la invitación de Catalina. En GitHub abre tu foto → Configuración → Correos electrónicos y verifica tu dirección. Instala [Git](https://git-scm.com/downloads/win), [VS Code](https://code.visualstudio.com/), [Python 3.14](https://www.python.org/downloads/) y [Node.js 24](https://nodejs.org/). Activa la opción de agregar Python al PATH si aparece. Cierra y abre VS Code después de instalar. El proyecto funciona con herramientas gratuitas.

**2. Abre una terminal.** En VS Code pulsa Ctrl+Shift+P, busca «Seleccionar perfil predeterminado» (Terminal: Select Default Profile) y elige **Símbolo del sistema / Command Prompt**. Abre **Terminal → Nuevo terminal**. Ejecuta cada línea. Debes ver cuatro versiones.

```cmd
git --version
python --version
node --version
npm --version
```

**3. Descarga el proyecto una sola vez.** Si ya tienes una copia, ábrela con **Archivo → Abrir carpeta**. Para crear una copia nueva:

```cmd
cd /d "%USERPROFILE%\Downloads"
git clone https://github.com/CataVega201/transmilenio-trip-planner.git
cd transmilenio-trip-planner
code .
```

Si `code .` no abre VS Code, usa **Archivo → Abrir carpeta** y elige la carpeta recién descargada. Abre un nuevo terminal allí. Debes ver README.md, servidor.py y frontend en el explorador.

**4. Configura TU autoría.** Sustituye ambos textos entre comillas por tus datos. Esta configuración aplica solo a esta copia. En tu primer push, inicia sesión con tu propia cuenta de GitHub.

```cmd
git config user.name "Tu nombre real"
git config user.email "Tu correo verificado en GitHub"
git config --get user.name
git config --get user.email
```

**5. Instala las dependencias.** Desde la carpeta del proyecto, una línea a la vez:

```cmd
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm --prefix frontend ci
```

**6. Comprueba la conexión.** En una terminal ejecuta `.\.venv\Scripts\python.exe servidor.py`. Déjala abierta. En otra ejecuta `npm --prefix frontend run dev`. Abre la dirección **Local** de Vite. Flask muestra su estado en http://127.0.0.1:5000/api/estado. El aviso de servidor de desarrollo es normal.

**7. Abre la IA.** En la **aplicación de escritorio de ChatGPT**, abre el selector de ChatGPT y elige **Codex** si está disponible. Abre el proyecto local y selecciona exactamente la carpeta que contiene servidor.py. Inicia sesión con tu cuenta personal. Puedes pedirle que compruebe o ejecute los pasos 4–6 si ya tiene acceso a la carpeta. [Guía oficial de OpenAI](https://developers.openai.com/codex/quickstart/).

Si usas el chat normal sin acceso a archivos o terminal, pega la guía y el contrato, pídele los archivos y comandos, y ejecútalos tú en VS Code. Si aparece un límite de uso, puedes seguir manualmente o retomar cuando vuelva tu acceso. No actives pagos ni pruebas de pago.
