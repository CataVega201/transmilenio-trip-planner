"""Adaptador HTTP del planeador. Cada instancia de Flask comparte una Red."""
from importlib import import_module
from pathlib import Path
from threading import RLock

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException
from motor.red import ModuloPendiente


# URL, operación pública y campos en su orden contractual.
CONSULTAS = [
    ("estaciones/estado", "estado", "nombre"),
    ("estaciones/autocompletar", "autocompletar", "prefijo k"),
    ("estaciones/rango", "rango", "desde hasta"),
    ("horarios/proximo", "proximo_bus", "estacion ruta hora"),
    ("viajes", "viaje", "origen destino"),
    ("ranking", "ranking", "k"),
    ("rutas/recorrido", "recorrido", "ruta al_reves"),
]
CAMBIOS = [
    ("rutas/agregar", "agregar_parada", "ruta nueva despues_de"),
    ("rutas/quitar", "quitar_parada", "ruta estacion"),
    ("estaciones/cerrar", "cerrar", "nombre"),
    ("estaciones/reabrir", "reabrir", "nombre"),
    ("historial/deshacer", "deshacer", ""),
    ("historial/rehacer", "rehacer", ""),
]


class Pendiente(Exception):
    """Una colaboración requerida aún no está integrada."""


class EntradaInvalida(Exception):
    """La petición no cumple el contrato del adaptador."""


def argumentos(datos, campos):
    valores = []
    for campo in campos.split():
        if campo == "al_reves":
            valor = datos.get(campo, "false")
            if valor not in ("true", "false"):
                raise EntradaInvalida("al_reves debe ser true o false")
            valores.append(valor == "true")
        elif campo == "k":
            try:
                valores.append(int(datos[campo]))
            except (KeyError, TypeError, ValueError) as error:
                raise EntradaInvalida from error
        else:
            try:
                valor = datos[campo]
            except KeyError as error:
                raise EntradaInvalida from error
            if not isinstance(valor, str):
                raise EntradaInvalida(f"{campo} debe ser texto")
            valores.append(valor)
    return valores


def crear_app(carpeta_datos=None, carpeta_web=None, *, red=None, simular=None, medir=None):
    app = Flask(__name__, static_folder=None)
    carpeta = Path(carpeta_datos or Path(__file__).with_name("datos"))
    bloqueo = RLock()

    def componente(nombre):
        try:
            modulo = import_module("motor")
        except ModuleNotFoundError as error:
            if error.name != "motor":
                raise
            raise Pendiente from error
        funcion = getattr(modulo, nombre, None)
        if funcion is None:
            raise Pendiente
        return funcion

    def ejecutar(operacion, campos, escritura):
        nonlocal red
        datos = request.get_json() if escritura else request.args
        if escritura and not isinstance(datos, dict):
            raise EntradaInvalida("Se esperaba un objeto JSON")
        args = argumentos(datos, campos)
        with bloqueo:
            if red is None:
                constructor = componente("Red")
                if not carpeta.is_dir():
                    raise Pendiente("Falta la carpeta de datos.")
                red = constructor(str(carpeta))
            funcion = getattr(red, operacion, None)
            if funcion is None:
                raise Pendiente
            return jsonify(ok=True, datos=funcion(*args))

    from functools import partial
    for escritura, rutas in [(False, CONSULTAS), (True, CAMBIOS)]:
        for url, operacion, campos in rutas:
            app.add_url_rule("/api/" + url, operacion,
                             partial(ejecutar, operacion, campos, escritura),
                             methods=["POST" if escritura else "GET"])

    @app.get("/api/estado")
    def salud():
        return jsonify(estado="ok", mensaje="Servidor de TransMilenio funcionando")

    @app.post("/api/fila")
    def fila():
        datos = request.get_json()
        if not isinstance(datos, dict):
            raise EntradaInvalida("Se esperaba un objeto JSON")
        funcion = simular or componente("simular_fila")
        try:
            argumentos_fila = datos["llegadas"], datos["frecuencia"], datos["capacidad"]
        except KeyError as error:
            raise EntradaInvalida from error
        return jsonify(ok=True, datos=funcion(*argumentos_fila))

    @app.post("/api/rendimiento")
    def rendimiento():
        if medir is None:
            raise Pendiente
        datos = request.get_json()
        if not isinstance(datos, dict):
            raise EntradaInvalida("Se esperaba un objeto JSON")
        try:
            argumentos_medicion = datos["tamanos"], datos["repeticiones"]
        except KeyError as error:
            raise EntradaInvalida from error
        return jsonify(ok=True, datos=medir(*argumentos_medicion))

    @app.errorhandler(Exception)
    def error(error):
        if isinstance(error, (Pendiente, ModuloPendiente)):
            estado, codigo = 503, "MODULO_PENDIENTE"
            mensaje = str(error) or "Esta función estará disponible al integrar el módulo del equipo."
        elif isinstance(error, EntradaInvalida) or (
            isinstance(error, HTTPException) and error.code in (400, 415)
        ):
            estado, codigo, mensaje = 400, "ENTRADA_INVALIDA", "Revisa los campos de la consulta."
        elif isinstance(error, HTTPException):
            estado, codigo, mensaje = error.code, "ERROR_HTTP", error.description
        else:
            app.logger.exception("Fallo al procesar la petición")
            estado, codigo, mensaje = 500, "ERROR_INTERNO", "No se pudo completar la operación."
        return jsonify(ok=False, error={"codigo": codigo, "mensaje": mensaje}), estado

    if carpeta_web:
        @app.get("/")
        def inicio():
            return send_from_directory(carpeta_web, "index.html")

        @app.get("/assets/<path:nombre>")
        def recurso(nombre):
            return send_from_directory(Path(carpeta_web) / "assets", nombre)
    return app


app = crear_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
