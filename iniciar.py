"""Arranque del planeador con un solo comando.

Uso (Windows, desde la carpeta del proyecto):
    .\\.venv\\Scripts\\python.exe iniciar.py --datos datos

Que hace:
1. Comprueba que Flask este instalado y que la carpeta de datos tenga los tres
   CSV del curso. Si algo falta, explica como resolverlo y se detiene.
2. Compila la pagina React (npm --prefix frontend run build). Si Node.js no
   esta instalado pero ya existe frontend/dist, usa esa compilacion y avisa.
3. Arranca un unico servidor local con la pagina y la API juntas.

No instala programas ni librerias por su cuenta: las instalaciones iniciales
estan en docs/INSTALACION.md.
"""

import argparse
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
FRONTEND = RAIZ / "frontend"
DIST = FRONTEND / "dist"
CSV_REQUERIDOS = ("estaciones.csv", "rutas.csv", "horarios.csv")


class ErrorArranque(Exception):
    """Problema que la persona puede resolver; se muestra sin traza."""


def leer_argumentos(argumentos=None):
    parser = argparse.ArgumentParser(
        description="Inicia el planeador de TransMilenio con un solo servidor.")
    parser.add_argument("--datos", default="datos",
                        help="carpeta con estaciones.csv, rutas.csv y horarios.csv (por defecto: datos)")
    parser.add_argument("--puerto", type=int, default=5000, help="puerto local (por defecto: 5000)")
    parser.add_argument("--sin-compilar", action="store_true",
                        help="usar frontend/dist tal como esta, sin volver a compilar")
    parser.add_argument("--no-abrir", action="store_true",
                        help="no abrir el navegador automaticamente")
    return parser.parse_args(argumentos)


def carpeta_de_datos(texto):
    """Ruta absoluta de los datos; relativa a la carpeta actual o al proyecto."""
    ruta = Path(texto).expanduser()
    if not ruta.is_absolute():
        en_actual = Path.cwd() / ruta
        ruta = en_actual if en_actual.exists() else RAIZ / ruta
    ruta = ruta.resolve()
    if not ruta.is_dir():
        raise ErrorArranque(f"No existe la carpeta de datos: {ruta}")
    faltan = [nombre for nombre in CSV_REQUERIDOS if not (ruta / nombre).is_file()]
    if faltan:
        raise ErrorArranque(
            f"En {ruta} faltan estos archivos: {', '.join(faltan)}. "
            "Revisa la carpeta o indica otra con --datos.")
    return ruta


def comprobar_flask():
    try:
        import flask  # noqa: F401
    except ImportError as error:
        raise ErrorArranque(
            "Flask no esta instalado en este Python. Activa el entorno del proyecto e "
            "instala las dependencias una vez con:\n"
            "  .\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt") from error


def compilar_pagina(sin_compilar):
    """Deja lista frontend/dist y devuelve su ruta."""
    if sin_compilar:
        if not (DIST / "index.html").is_file():
            raise ErrorArranque("Se pidio --sin-compilar pero no existe frontend/dist. "
                                "Quita esa opcion para compilar la pagina.")
        return DIST

    npm = shutil.which("npm")
    if npm is None:
        if (DIST / "index.html").is_file():
            print("Aviso: no se encontro Node.js (npm). Se usa la pagina compilada que ya "
                  "existe en frontend/dist; puede no tener los ultimos cambios.")
            return DIST
        raise ErrorArranque(
            "No se encontro Node.js (npm) y la pagina aun no esta compilada. Instala Node.js "
            "LTS desde https://nodejs.org y ejecuta una vez:\n"
            "  npm --prefix frontend install")
    if not (FRONTEND / "node_modules").is_dir():
        raise ErrorArranque("Faltan las dependencias de la pagina. Ejecuta una vez:\n"
                            "  npm --prefix frontend install")

    print("Compilando la pagina React...")
    resultado = subprocess.run([npm, "--prefix", str(FRONTEND), "run", "build"], cwd=RAIZ)
    if resultado.returncode != 0 or not (DIST / "index.html").is_file():
        raise ErrorArranque("La compilacion de la pagina fallo; revisa el mensaje de arriba.")
    return DIST


def funcion_de_medicion():
    """Medidor R11 para el panel, o None si aun no esta en esta copia."""
    try:
        from rendimiento.medir import medir_api
    except ImportError:
        return None
    return medir_api


def crear_aplicacion(datos, dist):
    if str(RAIZ) not in sys.path:
        sys.path.insert(0, str(RAIZ))
    from servidor import crear_app
    return crear_app(str(datos), str(dist), medir=funcion_de_medicion())


def main(argumentos=None):
    args = leer_argumentos(argumentos)
    try:
        comprobar_flask()
        datos = carpeta_de_datos(args.datos)
        dist = compilar_pagina(args.sin_compilar)
        app = crear_aplicacion(datos, dist)
    except ErrorArranque as error:
        print(f"\nNo se pudo iniciar: {error}", file=sys.stderr)
        return 1

    direccion = f"http://127.0.0.1:{args.puerto}/"
    print(f"\nDatos: {datos}")
    print(f"Planeador listo en {direccion}  (Ctrl + C para detener)\n")
    if not args.no_abrir:
        webbrowser.open(direccion)
    app.run(host="127.0.0.1", port=args.puerto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
