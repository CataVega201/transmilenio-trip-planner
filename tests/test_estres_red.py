"""Referencia independiente bajo miles de cambios mezclados de la red."""
import csv
import os
import random
import tempfile
import unittest
from pathlib import Path

from motor import Red


class EstresRed(unittest.TestCase):
    def test_cambios_aleatorios_con_oraculo_de_listas(self):
        azar = random.Random(212026)
        nombres = [f"Nodo {i:03d}" for i in range(80)]
        rutas = {f"Ruta {i:02d}": azar.sample(nombres, 12) for i in range(20)}
        eventos = {}
        filas_horas = []
        for ruta, paradas in rutas.items():
            for nombre in paradas:
                minutos = sorted([azar.randrange(1800) for _ in range(12)])
                minutos.append(minutos[0])  # Duplicados de buses válidos.
                eventos[(ruta, nombre)] = sorted(minutos)
                filas_horas += [(ruta, nombre, f"{t // 60:02d}:{t % 60:02d}") for t in minutos]
        with tempfile.TemporaryDirectory() as carpeta:
            for archivo, cabecera, filas in [
                ("estaciones.csv", ["nombre"], [(n,) for n in nombres]),
                ("rutas.csv", ["ruta", "orden", "estacion"],
                 [(r, i + 1, n) for r, ns in rutas.items() for i, n in enumerate(ns)]),
                ("horarios.csv", ["ruta", "estacion", "hora"], filas_horas),
            ]:
                azar.shuffle(filas)
                with (Path(carpeta) / archivo).open("w", encoding="utf-8", newline="") as f:
                    w = csv.writer(f)
                    w.writerow(cabecera)
                    w.writerows(filas)
            red = Red(carpeta)
            abiertas = dict.fromkeys(nombres, True)
            hechas, deshechas = [], []
            def foto():
                return abiertas.copy(), {r: ns[:] for r, ns in rutas.items()}

            pasos = int(os.environ.get("TM_ESTRES_PASOS", "1000"))
            for paso in range(pasos):
                operacion = azar.choice(["cerrar", "reabrir", "agregar_parada",
                                         "quitar_parada", "deshacer", "rehacer"])
                nombre = azar.choice(nombres + ["inexistente"])
                ruta = azar.choice(list(rutas) + ["inexistente"])
                anterior = azar.choice(nombres)
                antes = foto()
                if operacion == "deshacer":
                    esperado = bool(hechas)
                    if esperado:
                        accion = hechas.pop()
                        deshechas.append(accion)
                        abiertas = accion[0][0].copy()
                        rutas = {r: ns[:] for r, ns in accion[0][1].items()}
                    actual = red.deshacer()
                elif operacion == "rehacer":
                    esperado = bool(deshechas)
                    if esperado:
                        accion = deshechas.pop()
                        hechas.append(accion)
                        abiertas = accion[1][0].copy()
                        rutas = {r: ns[:] for r, ns in accion[1][1].items()}
                    actual = red.rehacer()
                elif operacion in ("cerrar", "reabrir"):
                    nuevo = operacion == "reabrir"
                    esperado = nombre in abiertas and abiertas[nombre] != nuevo
                    if esperado:
                        abiertas[nombre] = nuevo
                    actual = getattr(red, operacion)(nombre)
                elif operacion == "agregar_parada":
                    esperado = (ruta in rutas and nombre in abiertas
                                and nombre not in rutas[ruta] and anterior in rutas[ruta])
                    if esperado:
                        rutas[ruta].insert(rutas[ruta].index(anterior) + 1, nombre)
                    actual = red.agregar_parada(ruta, nombre, anterior)
                else:
                    esperado = ruta in rutas and nombre in rutas[ruta]
                    if esperado:
                        rutas[ruta].remove(nombre)
                    actual = red.quitar_parada(ruta, nombre)
                self.assertIs(actual, esperado, (paso, operacion))
                if esperado and operacion not in ("deshacer", "rehacer"):
                    hechas.append((antes, foto()))
                    deshechas.clear()

                # Cada paso comprueba consultas, no solo el resultado del cambio.
                disponibles = sorted(n for n in nombres if abiertas[n])
                k = azar.randrange(12)
                prefijo = azar.choice(["", "Nodo 0", "Nodo 00", "Z"])
                self.assertEqual(red.autocompletar(prefijo, k),
                                 [n for n in disponibles if n.startswith(prefijo)][:k])
                desde, hasta = azar.sample(nombres, 2)
                self.assertEqual(red.rango(desde, hasta),
                                 [n for n in disponibles if desde <= n <= hasta])
                conteos = dict.fromkeys(nombres, 0)
                for r, ns in rutas.items():
                    for n in ns:
                        conteos[n] += len(eventos.get((r, n), []))
                ranking = sorted([(n, conteos[n]) for n in disponibles],
                                 key=lambda par: (-par[1], par[0]))
                self.assertEqual(red.ranking(k), ranking[:k])
                minuto = azar.randrange(1800)
                buses = eventos.get((ruta, nombre), []) if (
                    ruta in rutas and nombre in rutas[ruta] and abiertas.get(nombre, False)) else []
                proximo = next((t for t in buses if t >= minuto), None)
                hora = f"{minuto // 60:02d}:{minuto % 60:02d}"
                texto = None if proximo is None else f"{proximo // 60:02d}:{proximo % 60:02d}"
                self.assertEqual(red.proximo_bus(nombre, ruta, hora), texto)
                if paso % 10 == 0:
                    origen, destino = azar.choice(nombres), azar.choice(nombres)
                    candidatos = []
                    if abiertas[origen] and abiertas[destino]:
                        for primera, ns in rutas.items():
                            if origen not in ns:
                                continue
                            a = ns.index(origen)
                            if destino in ns and ns.index(destino) > a:
                                candidatos.append(((ns.index(destino) - a, 0, primera, "", ""),
                                                   [(primera, origen, destino)]))
                            for cambio in ns[a + 1:]:
                                if not abiertas[cambio]:
                                    continue
                                for segunda, otras in rutas.items():
                                    if cambio in otras and destino in otras:
                                        b, c = otras.index(cambio), otras.index(destino)
                                        if c > b:
                                            costo = ns.index(cambio) - a + c - b
                                            candidatos.append(((costo, 1, primera, segunda, cambio),
                                                               [(primera, origen, cambio), (segunda, cambio, destino)]))
                    viaje = min(candidatos, default=(None, None), key=lambda par: par[0])[1]
                    if origen == destino and abiertas[origen]:
                        viaje = []
                    self.assertEqual(red.viaje(origen, destino), viaje)
                if paso % 25 == 0:
                    for n in nombres:
                        self.assertEqual(red.estado(n), "ABIERTA" if abiertas[n] else "CERRADA")
                    for r, ns in rutas.items():
                        self.assertEqual(red.recorrido(r), ns)
                        self.assertEqual(red.recorrido(r, True), ns[::-1])
            print(f"ESTRÉS: {pasos} cambios aleatorios y consultas cruzadas correctos.")
