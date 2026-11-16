"""Medicion de rendimiento R11, fuera del motor y sin pasar por HTTP.

Cada escenario dice:
- que requisito mide y que es n (pasajeros, estaciones, ...);
- como preparar el estado para un tamano n (fuera del tiempo medido);
- que operacion se cronometra.

Reglas de la guia que se cumplen aqui:
- Se separa preparacion, calentamiento y operacion.
- Se usa time.perf_counter_ns, varias repeticiones y la mediana.
- Las operaciones que cambian la red (cerrar, deshacer, ...) se preparan de
  nuevo antes de cada repeticion, fuera del tramo medido.
- Se informa la relacion con el tamano anterior (ideal: n y 2n).

Los escenarios que usan Red quedan como "pendiente" hasta que exista
`from motor import Red`; se activan solos cuando Alejandro la integre.

Uso desde la terminal:
    python -m rendimiento.medir --tamanos 50000 100000 200000
    python -m rendimiento.medir --solo R10 --json resultados.json
"""

import argparse
import json
import os
import statistics
import tempfile
import time

from rendimiento.generar import generar_llegadas, generar_red, nombre_estacion, nombre_ruta


class Escenario:
    """Una operacion a medir.

    - nombre: texto corto que se muestra en la tabla.
    - requisito: R1..R10 o "carga".
    - unidad: que significa n.
    - preparar(n, carpeta_tmp): devuelve el estado que recibe la operacion.
    - operacion(estado): lo unico que se cronometra.
    - mutable: si la operacion cambia el estado, se prepara de nuevo en
      cada repeticion.
    - necesita: "red" si depende de motor.Red.
    """

    def __init__(self, nombre, requisito, unidad, preparar, operacion,
                 mutable=False, necesita=None):
        self.nombre = nombre
        self.requisito = requisito
        self.unidad = unidad
        self.preparar = preparar
        self.operacion = operacion
        self.mutable = mutable
        self.necesita = necesita


def cronometrar(escenario, n, repeticiones, carpeta_tmp, calentamiento=1):
    """Devuelve la mediana en ns y las muestras de una operacion."""
    estado = escenario.preparar(n, carpeta_tmp)
    for _ in range(calentamiento):
        escenario.operacion(estado)
        if escenario.mutable:
            estado = escenario.preparar(n, carpeta_tmp)

    muestras = []
    salida = None
    for _ in range(repeticiones):
        if escenario.mutable:
            estado = escenario.preparar(n, carpeta_tmp)
        inicio = time.perf_counter_ns()
        salida = escenario.operacion(estado)
        muestras.append(time.perf_counter_ns() - inicio)

    tamano_salida = len(salida) if isinstance(salida, (list, tuple)) else None
    return statistics.median(muestras), muestras, tamano_salida


# --- Escenarios de R10 (ya disponibles) ---------------------------------

def _simular_fila():
    from motor.fila import simular_fila
    return simular_fila


def _escenarios_r10():
    def preparar_ordenadas(n, _carpeta):
        return generar_llegadas(n, ordenadas=True)

    def preparar_desordenadas(n, _carpeta):
        return generar_llegadas(n, ordenadas=False)

    def operacion(llegadas):
        return _simular_fila()(llegadas, 10, 3)

    return [
        Escenario("simular_fila ordenadas", "R10", "pasajeros",
                  preparar_ordenadas, operacion, necesita="fila"),
        Escenario("simular_fila desordenadas", "R10", "pasajeros",
                  preparar_desordenadas, operacion, necesita="fila"),
    ]


# --- Escenarios de Red (pendientes hasta que exista motor.Red) ----------

def _disponibles():
    """Que partes del motor existen ya en esta copia."""
    hay = []
    try:
        from motor.fila import simular_fila  # noqa: F401
        hay.append("fila")
    except ImportError:
        pass
    try:
        from motor import Red  # noqa: F401
        hay.append("red")
    except ImportError:
        pass
    return hay


def _crear_red(carpeta):
    from motor import Red
    return Red(carpeta)


def _carpeta_red(n, carpeta_tmp):
    """Genera (una sola vez por tamano) una red con n estaciones."""
    carpeta = os.path.join(carpeta_tmp, "red_%d" % n)
    if not os.path.isdir(carpeta):
        generar_red(carpeta, estaciones=n, rutas=max(1, n // 20))
    return carpeta


def _escenarios_red():
    def red(n, carpeta_tmp):
        return _crear_red(_carpeta_red(n, carpeta_tmp))

    medio = lambda n: nombre_estacion(max(1, n // 2))
    return [
        Escenario("Red(carpeta)", "carga", "estaciones",
                  lambda n, c: _carpeta_red(n, c),
                  _crear_red,
                  necesita="red"),
        Escenario("estado", "R1", "estaciones", lambda n, c: (red(n, c), medio(n)),
                  lambda e: e[0].estado(e[1]), necesita="red"),
        Escenario("autocompletar k=10", "R2", "estaciones", red,
                  lambda r: r.autocompletar("EST 0", 10), necesita="red"),
        Escenario("rango 100 nombres", "R3", "estaciones", lambda n, c: (red(n, c), n),
                  lambda e: e[0].rango(medio(e[1]), nombre_estacion(min(e[1], e[1] // 2 + 99))),
                  necesita="red"),
        Escenario("proximo_bus", "R4", "estaciones", red,
                  lambda r: r.proximo_bus(r.recorrido(nombre_ruta(1))[0], nombre_ruta(1), "05:00"),
                  necesita="red"),
        Escenario("ranking k=10", "R6", "estaciones", red,
                  lambda r: r.ranking(10), necesita="red"),
        Escenario("recorrido", "R7", "estaciones", red,
                  lambda r: r.recorrido(nombre_ruta(1)), necesita="red"),
        Escenario("recorrido al reves", "R7", "estaciones", red,
                  lambda r: r.recorrido(nombre_ruta(1), True), necesita="red"),
        Escenario("cerrar", "R8", "estaciones", lambda n, c: (red(n, c), medio(n)),
                  lambda e: e[0].cerrar(e[1]), mutable=True, necesita="red"),
        Escenario("deshacer un cierre", "R9", "estaciones",
                  lambda n, c: _red_con_cierre(red(n, c), medio(n)),
                  lambda r: r.deshacer(), mutable=True, necesita="red"),
    ]


def _red_con_cierre(red, nombre):
    red.cerrar(nombre)
    return red


def escenarios():
    return _escenarios_r10() + _escenarios_red()


# --- Ejecucion y presentacion -------------------------------------------

def medir(tamanos, repeticiones=5, solo=None):
    """Mide todos los escenarios y devuelve una lista de filas (dict)."""
    hay = _disponibles()
    faltan = {"fila": "pendiente: falta motor/fila.py (PR #8)",
              "red": "pendiente: falta motor.Red"}
    filas = []
    with tempfile.TemporaryDirectory(prefix="r11_") as carpeta_tmp:
        for escenario in escenarios():
            if solo and escenario.requisito != solo:
                continue
            if escenario.necesita and escenario.necesita not in hay:
                filas.append({"operacion": escenario.nombre,
                              "requisito": escenario.requisito,
                              "estado": faltan[escenario.necesita]})
                continue
            anterior = None
            for n in tamanos:
                mediana, muestras, salida = cronometrar(
                    escenario, n, repeticiones, carpeta_tmp)
                filas.append({
                    "operacion": escenario.nombre,
                    "requisito": escenario.requisito,
                    "estado": "medido",
                    "n": n,
                    "unidad": escenario.unidad,
                    "repeticiones": repeticiones,
                    "mediana_ns": int(mediana),
                    "min_ns": min(muestras),
                    "max_ns": max(muestras),
                    "tamano_salida": salida,
                    "relacion": None if anterior is None else round(mediana / anterior, 2),
                })
                anterior = mediana
    return filas


def imprimir(filas):
    print("%-26s %-6s %10s %-11s %12s %8s" % (
        "operacion", "req", "n", "unidad", "mediana", "x anterior"))
    for f in filas:
        if f["estado"] != "medido":
            print("%-26s %-6s %s" % (f["operacion"], f["requisito"], f["estado"]))
            continue
        relacion = "-" if f["relacion"] is None else "%.2f" % f["relacion"]
        print("%-26s %-6s %10d %-11s %12s %8s" % (
            f["operacion"], f["requisito"], f["n"], f["unidad"],
            formato_tiempo(f["mediana_ns"]), relacion))


def formato_tiempo(ns):
    """Muestra el tiempo en la unidad mas legible."""
    if ns < 10000:
        return "%d ns" % ns
    if ns < 10000000:
        return "%.1f us" % (ns / 1e3)
    return "%.1f ms" % (ns / 1e6)


def main(argumentos=None):
    parser = argparse.ArgumentParser(description="Mediciones R11 del motor.")
    parser.add_argument("--tamanos", type=int, nargs="+",
                        default=[50000, 100000, 200000])
    parser.add_argument("--repeticiones", type=int, default=5)
    parser.add_argument("--solo", help="medir solo un requisito, p. ej. R10")
    parser.add_argument("--json", help="archivo donde guardar los resultados")
    args = parser.parse_args(argumentos)

    filas = medir(args.tamanos, args.repeticiones, args.solo)
    imprimir(filas)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as salida:
            json.dump(filas, salida, ensure_ascii=False, indent=2)
        print("Resultados guardados en", args.json)


if __name__ == "__main__":
    main()
