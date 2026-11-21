"""Medicion de rendimiento R11, fuera del motor y sin pasar por HTTP.

Cada escenario dice:
- que requisito mide, que es n y que es k (si aplica);
- como preparar el estado para un tamano n (fuera del tiempo medido);
- que operacion se cronometra;
- como restaurar la red despues de una operacion que la cambia, tambien
  fuera del tiempo medido, para no medir miles de cierres de una estacion
  que ya quedo cerrada.

Reglas de la guia que se cumplen aqui:
- Se separa carga, preparacion, calentamiento y operacion.
- Se usa time.perf_counter_ns, varias repeticiones y la mediana.
- Se informa la relacion con el tamano anterior (ideal: n y 2n), el tamano de
  la salida, si la medicion es en cache caliente y lo que espera el autor.
- R5 se comprueba funcionalmente y se etiqueta aparte.

Los escenarios que usan Red quedan como "pendiente" hasta que exista
`from motor import Red`; se activan solos cuando se integre.

Uso desde la terminal:
    python -m rendimiento.medir
    python -m rendimiento.medir --tamanos 10000 20000 --solo R10 --json resultados.json

Uso desde el servidor (panel web): medir_api(tamanos, repeticiones).
"""

import argparse
import json
import os
import statistics
import tempfile
import time

from rendimiento.generar import generar_llegadas, generar_red, nombre_estacion, nombre_ruta

TAMANOS_ENTREGA = [10000, 20000, 40000, 80000]
LIMITE_TAMANO = 100000
LIMITE_TAMANOS = 5
LIMITE_REPETICIONES = 9
RUTA = nombre_ruta(1)


class Escenario:
    """Una operacion a medir.

    - nombre: texto corto que se muestra en la tabla.
    - requisito: R1..R10 o "carga".
    - unidad: que significa n.
    - preparar(n, contexto): devuelve el estado que recibe la operacion.
    - operacion(estado): lo unico que se cronometra.
    - restaurar(estado): deshace la operacion medida (fuera del tiempo medido).
    - limpiar(estado): al terminar, deshace lo que hizo preparar.
    - necesita: "fila" o "red" si depende de un modulo que puede faltar.
    - k: parametro de tamano de salida, si la operacion lo recibe.
    - esperado: complejidad que documenta el autor del requisito.
    - nota: aclaracion que acompana la fila del resultado.
    """

    def __init__(self, nombre, requisito, unidad, preparar, operacion,
                 restaurar=None, limpiar=None, necesita=None, k=None,
                 esperado="", nota=""):
        self.nombre = nombre
        self.requisito = requisito
        self.unidad = unidad
        self.preparar = preparar
        self.operacion = operacion
        self.restaurar = restaurar
        self.limpiar = limpiar
        self.necesita = necesita
        self.k = k
        self.esperado = esperado
        self.nota = nota


def cronometrar(escenario, n, repeticiones, contexto, calentamiento=1):
    """Devuelve la mediana en ns, las muestras y el tamano de la salida."""
    estado = escenario.preparar(n, contexto)
    for _ in range(calentamiento):
        escenario.operacion(estado)
        if escenario.restaurar:
            escenario.restaurar(estado)

    muestras = []
    salida = None
    for _ in range(repeticiones):
        inicio = time.perf_counter_ns()
        salida = escenario.operacion(estado)
        muestras.append(time.perf_counter_ns() - inicio)
        if escenario.restaurar:
            escenario.restaurar(estado)

    if escenario.limpiar:
        escenario.limpiar(estado)
    tamano_salida = len(salida) if isinstance(salida, (list, tuple)) else None
    return statistics.median(muestras), muestras, tamano_salida


# --- Disponibilidad de modulos -------------------------------------------

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


# --- Escenarios de R10 ----------------------------------------------------

def _simular(llegadas):
    from motor.fila import simular_fila
    return simular_fila(llegadas, 10, 3)


def _escenarios_r10():
    return [
        Escenario("simular_fila ordenadas", "R10", "pasajeros",
                  lambda n, c: generar_llegadas(n, ordenadas=True), _simular,
                  necesita="fila", esperado="O(n)",
                  nota="Llegadas ya ordenadas: no se reordena."),
        Escenario("simular_fila desordenadas", "R10", "pasajeros",
                  lambda n, c: generar_llegadas(n, ordenadas=False), _simular,
                  necesita="fila", esperado="O(n log n)",
                  nota="Incluye el merge sort propio de las llegadas."),
    ]


# --- Escenarios de Red ----------------------------------------------------

class Contexto:
    """Carpetas y redes por tamano, creadas una sola vez por medicion."""

    def __init__(self, carpeta_tmp):
        self.carpeta_tmp = carpeta_tmp
        self.redes = {}

    def carpeta(self, n):
        carpeta = os.path.join(self.carpeta_tmp, "red_%d" % n)
        if not os.path.isdir(carpeta):
            generar_red(carpeta, estaciones=n, rutas=max(1, n // 20))
        return carpeta

    def red(self, n):
        # Una red por tamano compartida por los escenarios: los que la
        # cambian la restauran, asi no se vuelve a cargar en cada repeticion.
        if n not in self.redes:
            self.redes[n] = _crear_red(self.carpeta(n))
        return self.redes[n]


def _crear_red(carpeta):
    from motor import Red
    return Red(carpeta)


def _medio(n):
    return nombre_estacion(max(1, n // 2))


def _parada_media(red):
    """(anterior, parada) en la mitad de la ruta 1, para quitar y restaurar."""
    paradas = red.recorrido(RUTA)
    i = len(paradas) // 2
    return paradas[i - 1], paradas[i]


def _fuera_de_ruta(red, n):
    """Una estacion que no esta en la ruta 1, para agregarla."""
    en_ruta = set(red.recorrido(RUTA))
    for i in range(1, n + 1):
        nombre = nombre_estacion(i)
        if nombre not in en_ruta:
            return nombre
    raise ValueError("todas las estaciones estan en la ruta")


def _escenarios_red():
    def con_red(extra=None):
        def preparar(n, c):
            red = c.red(n)
            return (red, extra(red, n)) if extra else red
        return preparar

    def preparar_deshacer(n, c):
        red = c.red(n)
        red.cerrar(_medio(n))
        return red

    def preparar_rehacer(n, c):
        red = preparar_deshacer(n, c)
        red.deshacer()
        return red

    def preparar_reabrir(n, c):
        red = c.red(n)
        red.cerrar(_medio(n))
        return red, _medio(n)

    def preparar_viaje(n, c):
        red = c.red(n)
        paradas = red.recorrido(RUTA)
        return red, paradas[0], paradas[-1]

    def preparar_rango(n, c):
        return c.red(n), _medio(n), nombre_estacion(min(n, n // 2 + 99))

    return [
        Escenario("Red(carpeta)", "carga", "estaciones",
                  lambda n, c: c.carpeta(n), _crear_red, necesita="red",
                  esperado="O(N + suma h log h)",
                  nota="Lee los tres CSV desde disco en cada repeticion."),
        Escenario("estado", "R1", "estaciones",
                  con_red(lambda r, n: _medio(n)), lambda e: e[0].estado(e[1]),
                  necesita="red", esperado="O(1) esperado"),
        Escenario("autocompletar", "R2", "estaciones", con_red(),
                  lambda r: r.autocompletar("EST 0", 10), necesita="red", k=10),
        Escenario("rango de 100 nombres", "R3", "estaciones", preparar_rango,
                  lambda e: e[0].rango(e[1], e[2]), necesita="red", k=100),
        Escenario("proximo_bus", "R4", "estaciones",
                  con_red(lambda r, n: r.recorrido(RUTA)[0]),
                  lambda e: e[0].proximo_bus(e[1], RUTA, "05:00"),
                  necesita="red", esperado="O(log h)"),
        Escenario("viaje (funcional)", "R5", "estaciones", preparar_viaje,
                  lambda e: e[0].viaje(e[1], e[2]), necesita="red",
                  nota="R5 se comprueba funcionalmente; su tiempo se reporta aparte."),
        Escenario("ranking", "R6", "estaciones", con_red(),
                  lambda r: r.ranking(10), necesita="red", k=10),
        Escenario("recorrido", "R7", "estaciones", con_red(),
                  lambda r: r.recorrido(RUTA), necesita="red", esperado="O(L)"),
        Escenario("recorrido al reves", "R7", "estaciones", con_red(),
                  lambda r: r.recorrido(RUTA, True), necesita="red", esperado="O(L)"),
        Escenario("agregar_parada", "R7", "estaciones",
                  con_red(lambda r, n: (_fuera_de_ruta(r, n), _parada_media(r)[0])),
                  lambda e: e[0].agregar_parada(RUTA, e[1][0], e[1][1]),
                  restaurar=lambda e: e[0].quitar_parada(RUTA, e[1][0]),
                  necesita="red", esperado="O(1) esperado",
                  nota="Se quita la parada fuera del tiempo medido."),
        Escenario("quitar_parada", "R7", "estaciones",
                  con_red(lambda r, n: _parada_media(r)),
                  lambda e: e[0].quitar_parada(RUTA, e[1][1]),
                  restaurar=lambda e: e[0].agregar_parada(RUTA, e[1][1], e[1][0]),
                  necesita="red", esperado="O(1) esperado",
                  nota="Se vuelve a agregar fuera del tiempo medido."),
        Escenario("cerrar", "R8", "estaciones",
                  con_red(lambda r, n: _medio(n)), lambda e: e[0].cerrar(e[1]),
                  restaurar=lambda e: e[0].reabrir(e[1]), necesita="red",
                  nota="Se reabre fuera del tiempo medido."),
        Escenario("reabrir", "R8", "estaciones", preparar_reabrir,
                  lambda e: e[0].reabrir(e[1]),
                  restaurar=lambda e: e[0].cerrar(e[1]),
                  limpiar=lambda e: e[0].reabrir(e[1]), necesita="red",
                  nota="Se vuelve a cerrar fuera del tiempo medido."),
        Escenario("deshacer un cierre", "R9", "estaciones", preparar_deshacer,
                  lambda r: r.deshacer(), restaurar=lambda r: r.rehacer(),
                  limpiar=lambda r: r.deshacer(), necesita="red", esperado="O(1)"),
        Escenario("rehacer un cierre", "R9", "estaciones", preparar_rehacer,
                  lambda r: r.rehacer(), restaurar=lambda r: r.deshacer(),
                  necesita="red", esperado="O(1)"),
    ]


def escenarios():
    return _escenarios_r10() + _escenarios_red()


# --- Ejecucion y presentacion --------------------------------------------

FALTAN = {
    "fila": "pendiente: falta motor/fila.py",
    "red": "pendiente: falta motor.Red",
}


def medir(tamanos, repeticiones=5, solo=None):
    """Mide todos los escenarios y devuelve una lista de filas (dict).

    Cada fila medida tiene: operacion, requisito, estado ("medido"), n,
    unidad, k, repeticiones, mediana_ns, min_ns, max_ns, tamano_salida,
    relacion (mediana / mediana del tamano anterior), cache, esperado y nota.
    Las filas no medidas solo tienen operacion, requisito, estado y nota.
    """
    hay = _disponibles()
    filas = []
    with tempfile.TemporaryDirectory(prefix="r11_") as carpeta_tmp:
        contexto = Contexto(carpeta_tmp)
        for escenario in escenarios():
            if solo and escenario.requisito != solo:
                continue
            base = {"operacion": escenario.nombre, "requisito": escenario.requisito,
                    "esperado": escenario.esperado, "nota": escenario.nota}
            if escenario.necesita and escenario.necesita not in hay:
                filas.append(dict(base, estado=FALTAN[escenario.necesita]))
                continue
            anterior = None
            for n in tamanos:
                try:
                    mediana, muestras, salida = cronometrar(
                        escenario, n, repeticiones, contexto)
                except Exception as error:  # el autor debe revisar su operacion
                    filas.append(dict(base, estado="error: %s" % error, n=n))
                    anterior = None
                    continue
                filas.append(dict(
                    base,
                    estado="medido",
                    n=n,
                    unidad=escenario.unidad,
                    k=escenario.k,
                    repeticiones=repeticiones,
                    mediana_ns=int(mediana),
                    min_ns=min(muestras),
                    max_ns=max(muestras),
                    tamano_salida=salida,
                    relacion=None if not anterior else round(mediana / anterior, 2),
                    cache="caliente (tras calentamiento)",
                ))
                anterior = mediana
    return filas


def medir_api(tamanos, repeticiones):
    """Entrada para el panel web: valida limites y llama a medir.

    El servidor la recibe como crear_app(medir=medir_api). Los limites evitan
    que una sola peticion bloquee el servidor por minutos.
    """
    if (not isinstance(tamanos, list) or not 1 <= len(tamanos) <= LIMITE_TAMANOS
            or any(isinstance(n, bool) or not isinstance(n, int)
                   or not 1 <= n <= LIMITE_TAMANO for n in tamanos)):
        raise ValueError("tamanos debe ser una lista de 1 a %d enteros entre 1 y %d"
                         % (LIMITE_TAMANOS, LIMITE_TAMANO))
    if (isinstance(repeticiones, bool) or not isinstance(repeticiones, int)
            or not 1 <= repeticiones <= LIMITE_REPETICIONES):
        raise ValueError("repeticiones debe ser un entero entre 1 y %d"
                         % LIMITE_REPETICIONES)
    return medir(tamanos, repeticiones)


def imprimir(filas):
    print("%-26s %-6s %8s %-11s %12s %8s" % (
        "operacion", "req", "n", "unidad", "mediana", "x anterior"))
    for f in filas:
        if f["estado"] != "medido":
            print("%-26s %-6s %s" % (f["operacion"], f["requisito"], f["estado"]))
            continue
        relacion = "-" if f["relacion"] is None else "%.2f" % f["relacion"]
        print("%-26s %-6s %8d %-11s %12s %8s" % (
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
    parser.add_argument("--tamanos", type=int, nargs="+", default=TAMANOS_ENTREGA)
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
