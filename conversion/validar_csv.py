"""Valida los tres CSV sin modificarlos. Se ejecuta fuera de motor/."""

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


def validar(carpeta):
    carpeta = Path(carpeta)
    problemas = Counter()
    ejemplos = defaultdict(list)
    resumen = {}

    def problema(tipo, detalle):
        problemas[tipo] += 1
        if len(ejemplos[tipo]) < 5:
            ejemplos[tipo].append(detalle)

    def leer(nombre, encabezado):
        with (carpeta / nombre).open(encoding="utf-8-sig", newline="") as archivo:
            lector = csv.reader(archivo)
            if next(lector, None) != encabezado:
                problema("encabezado", nombre)
                return
            for fila in lector:
                numero = lector.line_num
                if len(fila) != len(encabezado):
                    problema("columnas", f"{nombre}:{numero}")
                    continue
                yield numero, fila

    def nombre_valido(nombre):
        # La ENE con virgulilla es una letra propia; no se elimina.
        sin_acentos = ''.join(c for c in unicodedata.normalize(
            'NFD', nombre.replace('Ñ', '\0')) if not unicodedata.combining(c))
        return bool(nombre) and nombre == nombre.strip().upper() and (
            nombre == sin_acentos.replace('\0', 'Ñ'))

    estaciones = set()
    total_estaciones = 0
    for numero, (nombre,) in leer("estaciones.csv", ["nombre"]):
        total_estaciones += 1
        if not nombre_valido(nombre):
            problema("nombre_no_normalizado", f"estaciones.csv:{numero}: {nombre}")
        if nombre in estaciones:
            problema("estacion_duplicada", f"estaciones.csv:{numero}: {nombre}")
        estaciones.add(nombre)

    recorridos = defaultdict(list)
    ordenes = set()
    parejas = set()
    total_paradas = 0
    for numero, (ruta, orden, estacion) in leer(
        "rutas.csv", ["ruta", "orden", "estacion"]
    ):
        total_paradas += 1
        if not nombre_valido(ruta):
            problema("ruta_no_normalizada", f"rutas.csv:{numero}: {ruta}")
        if estacion not in estaciones:
            problema("parada_desconocida", f"rutas.csv:{numero}: {estacion}")
        if not re.fullmatch(r"[0-9]+", orden) or int(orden) < 1:
            problema("orden_invalido", f"rutas.csv:{numero}: {orden}")
            continue
        posicion = int(orden)
        if (ruta, posicion) in ordenes:
            problema("orden_duplicado", f"rutas.csv:{numero}: {ruta}/{orden}")
        if (ruta, estacion) in parejas:
            problema("parada_repetida_en_ruta", f"rutas.csv:{numero}: {ruta}/{estacion}")
        ordenes.add((ruta, posicion))
        parejas.add((ruta, estacion))
        recorridos[ruta].append(posicion)

    saltos = 0
    for posiciones in recorridos.values():
        if sorted(posiciones) != list(range(1, len(posiciones) + 1)):
            saltos += 1

    eventos = Counter()
    total_horarios = 0
    extendidos = 0
    menor = None
    mayor = None
    parejas_con_horarios = set()
    for numero, (ruta, estacion, hora) in leer(
        "horarios.csv", ["ruta", "estacion", "hora"]
    ):
        total_horarios += 1
        if (ruta, estacion) not in parejas:
            problema("horario_fuera_de_recorrido", f"horarios.csv:{numero}: {ruta}/{estacion}")
        if not re.fullmatch(r"[0-9]{2,}:[0-5][0-9]", hora):
            problema("hora_invalida", f"horarios.csv:{numero}: {hora}")
            continue
        minutos = int(hora[:-3]) * 60 + int(hora[-2:])
        extendidos += minutos >= 1440
        menor = minutos if menor is None else min(menor, minutos)
        mayor = minutos if mayor is None else max(mayor, minutos)
        eventos[(ruta, estacion, hora)] += 1
        parejas_con_horarios.add((ruta, estacion))

    resumen.update(
        estaciones=total_estaciones, estaciones_unicas=len(estaciones),
        rutas=len(recorridos), paradas_en_rutas=total_paradas,
        horarios=total_horarios, horarios_desde_24h=extendidos,
        minuto_minimo=menor, minuto_maximo=mayor,
        eventos_identicos_adicionales=sum(c - 1 for c in eventos.values()),
        parejas_sin_horarios=len(parejas - parejas_con_horarios),
        rutas_con_orden_no_consecutivo=saltos,
        estaciones_sin_ruta=len(estaciones - {e for _, e in parejas}),
    )
    return {"valido_segun_acuerdos": not problemas, "resumen": resumen,
            "problemas": dict(problemas), "ejemplos": dict(ejemplos)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("carpeta", type=Path, help="Carpeta con los tres CSV")
    args = parser.parse_args()
    try:
        resultado = validar(args.carpeta)
    except (OSError, UnicodeError, csv.Error) as error:
        parser.exit(2, f"No se pudieron leer los CSV: {error}\n")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0 if resultado["valido_segun_acuerdos"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
