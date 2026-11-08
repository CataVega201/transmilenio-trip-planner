"""Convierte un ZIP GTFS estático en los tres CSV del planeador."""
import argparse
import csv
from collections import defaultdict
from datetime import date
from io import TextIOWrapper
from pathlib import Path, PurePosixPath
import re
from tempfile import TemporaryDirectory
import unicodedata
from zipfile import BadZipFile, ZipFile

if __package__:
    from .validar_csv import validar
else:
    from validar_csv import validar


def filas(zip_gtfs, archivo, campos, opcional=False):
    entradas = [p for p in zip_gtfs.namelist()
                if PurePosixPath(p).name == archivo and "__MACOSX" not in PurePosixPath(p).parts]
    if not entradas and opcional:
        return
    if len(entradas) != 1:
        raise ValueError(f"Se requiere una sola copia de {archivo}")
    with zip_gtfs.open(entradas[0]) as entrada, TextIOWrapper(entrada, encoding="utf-8-sig", newline="") as texto:
        lector = csv.DictReader(texto)
        faltantes = set(campos.split()) - set(lector.fieldnames or [])
        if faltantes:
            raise ValueError(f"{archivo}: faltan columnas {sorted(faltantes)}")
        yield from lector


def servicios_activos(zip_gtfs, fecha):
    dias = "monday tuesday wednesday thursday friday saturday sunday".split()
    dia = dias[fecha.weekday()]
    clave = fecha.strftime("%Y%m%d")
    activos = set()
    for f in filas(zip_gtfs, "calendar.txt", f"service_id start_date end_date {dia}", opcional=True):
        if f["start_date"] <= clave <= f["end_date"] and f[dia] == "1":
            activos.add(f["service_id"])
    for f in filas(zip_gtfs, "calendar_dates.txt", "service_id date exception_type", opcional=True):
        if f["date"] == clave:
            if f["exception_type"] == "1":
                activos.add(f["service_id"])
            elif f["exception_type"] == "2":
                activos.discard(f["service_id"])
            else:
                raise ValueError("Excepción de calendario desconocida")
    if not activos:
        raise ValueError(f"No hay servicios activos para {fecha}")
    return activos


def normalizar(nombre):
    nombre = " ".join(unicodedata.normalize("NFC", nombre).upper().split())
    return "".join(c if c == "Ñ" else "".join(x for x in unicodedata.normalize("NFD", c)
                   if not unicodedata.combining(x)) for c in nombre)


def recoger(zip_gtfs, fecha, solo_troncal=False):
    activos = servicios_activos(zip_gtfs, fecha)
    rutas = {f["route_id"]: f for f in filas(zip_gtfs, "routes.txt", "route_id")}
    if solo_troncal and not any(f.get("route_desc") == "TRONCAL" for f in rutas.values()):
        raise ValueError("El archivo no identifica rutas TRONCAL en route_desc")
    viajes = {}
    for f in filas(zip_gtfs, "trips.txt", "trip_id route_id service_id"):
        if f["service_id"] in activos:
            if f["route_id"] not in rutas or f["trip_id"] in viajes:
                raise ValueError(f"Viaje con ruta desconocida o ID repetido: {f['trip_id']}")
            if solo_troncal and rutas[f["route_id"]]["route_desc"] != "TRONCAL":
                continue
            viajes[f["trip_id"]] = (f["route_id"], f.get("direction_id") or "X")
    for f in filas(zip_gtfs, "frequencies.txt", "trip_id", opcional=True):
        if f["trip_id"] in viajes:
            raise ValueError("Hay servicios activos por frecuencia: esta versión requiere horarios explícitos.")
    paradas = {f["stop_id"]: f for f in filas(zip_gtfs, "stops.txt", "stop_id stop_name")}
    nombres = {}
    por_viaje = defaultdict(list)
    for f in filas(zip_gtfs, "stop_times.txt", "trip_id stop_id stop_sequence arrival_time departure_time"):
        viaje = f["trip_id"]
        if viaje not in viajes:
            continue
        parada = paradas[f["stop_id"]]
        id_estacion = parada.get("parent_station") or parada["stop_id"]
        nombre = normalizar(paradas[id_estacion]["stop_name"])
        if solo_troncal and not parada.get("parent_station"):
            # El feed de 2021 codifica el vagón o plataforma como sufijo.
            base = re.sub(r"\s+(?:[A-Z]\s*-\s*[0-9]+(?:\s+O\s+[0-9]+)?|T-?\d+\s*[A-Z]?)$", "", nombre)
            if base != nombre:
                nombre, id_estacion = base, "TRONCAL:" + base
        if not nombre or nombres.setdefault(nombre, id_estacion) != id_estacion:
            raise ValueError(f"Estaciones distintas con el mismo nombre o nombre vacío: {nombre!r}")
        hora = f["departure_time"] or f["arrival_time"]
        if not re.fullmatch(r"[0-9]+:[0-5][0-9]:[0-5][0-9]", hora):
            raise ValueError(f"Hora ausente o inválida en viaje {viaje}: {hora!r}")
        h, m, _ = hora.split(":")
        por_viaje[viaje].append((int(f["stop_sequence"]), nombre, f"{int(h):02d}:{m}"))
    if not viajes or viajes.keys() != por_viaje.keys():
        raise ValueError("Faltan paradas para viajes del día seleccionado")
    patrones = defaultdict(list)
    for viaje, eventos in por_viaje.items():
        eventos.sort()
        if len({n for n, _, _ in eventos}) != len(eventos):
            raise ValueError(f"Secuencia repetida: {viaje}")
        if solo_troncal:
            visitas = []
            for evento in eventos:
                if visitas and visitas[-1][1] == evento[1]:
                    visitas[-1] = evento
                else:
                    visitas.append(evento)
            eventos = visitas
        recorrido = tuple(nombre for _, nombre, _ in eventos)
        if len(set(recorrido)) != len(recorrido):
            raise ValueError(f"Viaje {viaje}: estación o secuencia repetida; revisar el recorrido")
        patrones[(*viajes[viaje], recorrido)].append(eventos)
    return patrones


def escribir(carpeta, patrones):
    nombres = {nombre for _, _, recorrido in patrones for nombre in recorrido}
    with (carpeta / "estaciones.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["nombre"])
        writer.writerows([nombre] for nombre in sorted(nombres))
    identificadores = set()
    with (carpeta / "rutas.csv").open("w", encoding="utf-8", newline="") as rutas, (
         carpeta / "horarios.csv").open("w", encoding="utf-8", newline="") as horarios:
        r, h = csv.writer(rutas), csv.writer(horarios)
        r.writerow(["ruta", "orden", "estacion"])
        h.writerow(["ruta", "estacion", "hora"])
        variantes = defaultdict(int)
        for clave in sorted(patrones):
            ruta, sentido, recorrido = clave
            variantes[ruta, sentido] += 1
            etiqueta = f"{normalizar(ruta)}-{sentido}-{variantes[ruta, sentido]}"
            if etiqueta in identificadores:
                raise ValueError(f"Colisión de identificadores de ruta: {etiqueta}")
            identificadores.add(etiqueta)
            r.writerows((etiqueta, i, nombre) for i, nombre in enumerate(recorrido, 1))
            for eventos in patrones[clave]:
                h.writerows((etiqueta, nombre, hora) for _, nombre, hora in eventos)


def convertir(archivo, destino, fecha, solo_troncal=False):
    destino = Path(destino)
    if destino.exists():
        raise ValueError("Elige una carpeta de salida nueva para conservar los datos existentes")
    with ZipFile(archivo) as zip_gtfs:
        patrones = recoger(zip_gtfs, fecha, solo_troncal)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=destino.parent) as temporal:
        carpeta = Path(temporal) / "resultado"
        carpeta.mkdir()
        escribir(carpeta, patrones)
        resultado = validar(carpeta)
        if not resultado["valido_segun_acuerdos"]:
            raise ValueError(f"Falló la validación: {resultado['ejemplos']}")
        carpeta.rename(destino)
    return resultado["resumen"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip", type=Path)
    parser.add_argument("salida", type=Path)
    parser.add_argument("--fecha", type=date.fromisoformat, required=True, metavar="AAAA-MM-DD")
    parser.add_argument("--troncal", action="store_true", help="Solo servicios TRONCAL del GTFS de Bogotá")
    args = parser.parse_args()
    try:
        resumen = convertir(args.zip, args.salida, args.fecha, args.troncal)
    except (ValueError, KeyError, OSError, BadZipFile, csv.Error) as error:
        parser.exit(1, f"Conversión interrumpida: {error}\n")
    print(f"{resumen['rutas']} rutas, {resumen['estaciones']} estaciones, {resumen['horarios']} horarios")
