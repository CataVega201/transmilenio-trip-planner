"""Generador de redes sinteticas para las mediciones de R11.

Crea una carpeta con los tres CSV del formato del curso:

- estaciones.csv: nombre
- rutas.csv:      ruta,orden,estacion
- horarios.csv:   ruta,estacion,hora

Los nombres son inventados (EST 000001, R0001, ...) para no confundirlos con
la red real. Con la misma semilla y los mismos tamanos el resultado es
identico, asi se pueden comparar ensayos.

Este modulo esta fuera de motor/ y puede usar cualquier herramienta.

Uso desde la terminal:
    python -m rendimiento.generar CARPETA --estaciones 1000 --rutas 50
"""

import argparse
import csv
import os
import random

ENCABEZADOS = {
    "estaciones.csv": ["nombre"],
    "rutas.csv": ["ruta", "orden", "estacion"],
    "horarios.csv": ["ruta", "estacion", "hora"],
}


def nombre_estacion(i):
    return "EST %06d" % i


def nombre_ruta(i):
    return "R%04d" % i


def hora_texto(minutos):
    """Convierte minutos del dia de servicio a HH:MM (admite horas > 23)."""
    return "%02d:%02d" % (minutos // 60, minutos % 60)


def generar_red(carpeta, estaciones, rutas, paradas_por_ruta=None,
                buses_por_parada=4, semilla=2026):
    """Escribe una red sintetica en `carpeta` y devuelve un resumen.

    - estaciones: cuantas estaciones distintas tiene la red.
    - rutas: cuantas rutas (cada una representa un solo sentido).
    - paradas_por_ruta: paradas de cada ruta; por defecto min(20, estaciones).
      Una estacion aparece como maximo una vez en cada ruta.
    - buses_por_parada: filas de horarios por cada pareja ruta-estacion.
      Pueden repetirse horas: el contrato las cuenta como buses distintos.
    - semilla: fija el azar para que el resultado sea reproducible.

    Las filas de rutas.csv y horarios.csv se escriben mezcladas, porque el
    motor no debe suponer que vienen ordenadas.
    """
    if estaciones < 1 or rutas < 0 or buses_por_parada < 0:
        raise ValueError("tamanos invalidos")
    if paradas_por_ruta is None:
        paradas_por_ruta = min(20, estaciones)
    if not 1 <= paradas_por_ruta <= estaciones:
        raise ValueError("paradas_por_ruta debe estar entre 1 y estaciones")

    azar = random.Random(semilla)
    os.makedirs(carpeta, exist_ok=True)

    nombres = [nombre_estacion(i) for i in range(1, estaciones + 1)]
    filas_rutas = []
    filas_horarios = []
    for r in range(1, rutas + 1):
        ruta = nombre_ruta(r)
        paradas = azar.sample(nombres, paradas_por_ruta)
        salida = azar.randint(4 * 60, 22 * 60)          # primer bus del dia
        for orden, estacion in enumerate(paradas, start=1):
            filas_rutas.append([ruta, orden, estacion])
            for b in range(buses_por_parada):
                # Cada parada queda unos minutos despues de la anterior; los
                # buses de la ruta se separan entre 5 y 15 minutos.
                minuto = salida + orden * 2 + b * azar.randint(5, 15)
                filas_horarios.append([ruta, estacion, hora_texto(minuto)])

    azar.shuffle(nombres)
    azar.shuffle(filas_rutas)
    azar.shuffle(filas_horarios)

    _escribir(carpeta, "estaciones.csv", [[n] for n in nombres])
    _escribir(carpeta, "rutas.csv", filas_rutas)
    _escribir(carpeta, "horarios.csv", filas_horarios)

    return {
        "carpeta": carpeta,
        "estaciones": estaciones,
        "rutas": rutas,
        "paradas": len(filas_rutas),
        "horarios": len(filas_horarios),
        "semilla": semilla,
    }


def _escribir(carpeta, archivo, filas):
    ruta = os.path.join(carpeta, archivo)
    with open(ruta, "w", encoding="utf-8", newline="") as salida:
        escritor = csv.writer(salida)
        escritor.writerow(ENCABEZADOS[archivo])
        escritor.writerows(filas)


def generar_llegadas(pasajeros, semilla=2026, ordenadas=True, horizonte=None):
    """Lista de segundos de llegada para medir R10."""
    azar = random.Random(semilla)
    if horizonte is None:
        horizonte = pasajeros
    llegadas = [azar.randint(0, horizonte) for _ in range(pasajeros)]
    if ordenadas:
        llegadas.sort()
    return llegadas


def main(argumentos=None):
    parser = argparse.ArgumentParser(description="Genera una red sintetica.")
    parser.add_argument("carpeta")
    parser.add_argument("--estaciones", type=int, default=1000)
    parser.add_argument("--rutas", type=int, default=50)
    parser.add_argument("--paradas", type=int, default=None)
    parser.add_argument("--buses", type=int, default=4)
    parser.add_argument("--semilla", type=int, default=2026)
    args = parser.parse_args(argumentos)
    resumen = generar_red(args.carpeta, args.estaciones, args.rutas,
                          args.paradas, args.buses, args.semilla)
    print("Red generada en %(carpeta)s: %(estaciones)d estaciones, "
          "%(rutas)d rutas, %(paradas)d paradas, %(horarios)d horarios "
          "(semilla %(semilla)d)" % resumen)


if __name__ == "__main__":
    main()
