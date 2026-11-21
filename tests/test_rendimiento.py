"""Pruebas de la infraestructura R11 (generador y medidor).

Ejecutar desde la carpeta del proyecto:
    .\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_rendimiento.py" -v
"""

import csv
import os
import tempfile
import unittest

from rendimiento import medir as medidor
from rendimiento.generar import generar_llegadas, generar_red, hora_texto


def leer(carpeta, archivo):
    with open(os.path.join(carpeta, archivo), encoding="utf-8", newline="") as f:
        return list(csv.reader(f))


class PruebasGenerador(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.carpeta = os.path.join(self.tmp.name, "red con espacios")

    def tearDown(self):
        self.tmp.cleanup()

    def test_encabezados_exactos(self):
        generar_red(self.carpeta, estaciones=30, rutas=3)
        self.assertEqual(leer(self.carpeta, "estaciones.csv")[0], ["nombre"])
        self.assertEqual(leer(self.carpeta, "rutas.csv")[0], ["ruta", "orden", "estacion"])
        self.assertEqual(leer(self.carpeta, "horarios.csv")[0], ["ruta", "estacion", "hora"])

    def test_cantidades(self):
        resumen = generar_red(self.carpeta, estaciones=50, rutas=4,
                              paradas_por_ruta=10, buses_por_parada=3)
        self.assertEqual(len(leer(self.carpeta, "estaciones.csv")) - 1, 50)
        self.assertEqual(len(leer(self.carpeta, "rutas.csv")) - 1, 40)
        self.assertEqual(len(leer(self.carpeta, "horarios.csv")) - 1, 120)
        self.assertEqual(resumen["paradas"], 40)
        self.assertEqual(resumen["horarios"], 120)

    def test_misma_semilla_mismo_resultado(self):
        otra = os.path.join(self.tmp.name, "otra")
        generar_red(self.carpeta, 40, 5, semilla=9)
        generar_red(otra, 40, 5, semilla=9)
        for archivo in ("estaciones.csv", "rutas.csv", "horarios.csv"):
            self.assertEqual(leer(self.carpeta, archivo), leer(otra, archivo))

    def test_referencias_validas_y_sin_repetir_en_ruta(self):
        generar_red(self.carpeta, estaciones=40, rutas=6, paradas_por_ruta=15)
        nombres = set(fila[0] for fila in leer(self.carpeta, "estaciones.csv")[1:])
        self.assertEqual(len(nombres), 40)  # estaciones unicas
        por_ruta = {}
        for ruta, orden, estacion in leer(self.carpeta, "rutas.csv")[1:]:
            self.assertIn(estacion, nombres)
            por_ruta.setdefault(ruta, []).append((int(orden), estacion))
        for ruta, paradas in por_ruta.items():
            ordenes = sorted(o for o, _ in paradas)
            self.assertEqual(ordenes, list(range(1, len(paradas) + 1)))
            estaciones = [e for _, e in paradas]
            self.assertEqual(len(estaciones), len(set(estaciones)))
        pares = set((r, e) for r, lista in por_ruta.items() for _, e in lista)
        for ruta, estacion, _hora in leer(self.carpeta, "horarios.csv")[1:]:
            self.assertIn((ruta, estacion), pares)

    def test_horas_validas(self):
        generar_red(self.carpeta, estaciones=30, rutas=5)
        for _ruta, _estacion, hora in leer(self.carpeta, "horarios.csv")[1:]:
            horas, minutos = hora.split(":")
            self.assertGreaterEqual(len(horas), 2)
            self.assertEqual(len(minutos), 2)
            self.assertTrue(0 <= int(minutos) <= 59)

    def test_hora_texto_admite_mas_de_24(self):
        self.assertEqual(hora_texto(1510), "25:10")
        self.assertEqual(hora_texto(65), "01:05")

    def test_tamanos_invalidos(self):
        with self.assertRaises(ValueError):
            generar_red(self.carpeta, estaciones=0, rutas=1)
        with self.assertRaises(ValueError):
            generar_red(self.carpeta, estaciones=5, rutas=1, paradas_por_ruta=6)

    def test_llegadas(self):
        ordenadas = generar_llegadas(1000, semilla=3)
        self.assertEqual(len(ordenadas), 1000)
        self.assertEqual(ordenadas, sorted(ordenadas))
        self.assertEqual(ordenadas, generar_llegadas(1000, semilla=3))
        mezcladas = generar_llegadas(1000, semilla=3, ordenadas=False)
        self.assertEqual(sorted(mezcladas), ordenadas)


class RedFalsa:
    """Red minima que cumple el contrato, solo para probar el medidor."""

    def __init__(self, carpeta):
        self.estaciones = sorted(f[0] for f in leer(carpeta, "estaciones.csv")[1:])
        self.rutas = {}
        for ruta, orden, estacion in sorted(leer(carpeta, "rutas.csv")[1:],
                                            key=lambda f: (f[0], int(f[1]))):
            self.rutas.setdefault(ruta, []).append(estacion)
        self.cerradas = set()
        self.hechas, self.deshechas = [], []

    def estado(self, nombre):
        if nombre not in self.estaciones:
            return "NO EXISTE"
        return "CERRADA" if nombre in self.cerradas else "ABIERTA"

    def autocompletar(self, prefijo, k):
        return [e for e in self.estaciones if e.startswith(prefijo)][:k]

    def rango(self, desde, hasta):
        return [e for e in self.estaciones if desde <= e <= hasta]

    def proximo_bus(self, estacion, ruta, hora):
        return "05:10"

    def viaje(self, origen, destino):
        return [("R0001", origen, destino)]

    def ranking(self, k):
        return [(e, 1) for e in self.estaciones[:k]]

    def recorrido(self, ruta, al_reves=False):
        lista = list(self.rutas.get(ruta, []))
        return lista[::-1] if al_reves else lista

    def agregar_parada(self, ruta, nueva, despues_de):
        lista = self.rutas[ruta]
        if nueva in lista or despues_de not in lista:
            return False
        lista.insert(lista.index(despues_de) + 1, nueva)
        return True

    def quitar_parada(self, ruta, estacion):
        lista = self.rutas[ruta]
        if estacion not in lista:
            return False
        lista.remove(estacion)
        return True

    def _cambiar(self, nombre, cerrar):
        if nombre not in self.estaciones or (nombre in self.cerradas) == cerrar:
            return False
        (self.cerradas.add if cerrar else self.cerradas.discard)(nombre)
        self.hechas.append((nombre, cerrar))
        self.deshechas.clear()
        return True

    def cerrar(self, nombre):
        return self._cambiar(nombre, True)

    def reabrir(self, nombre):
        return self._cambiar(nombre, False)

    def deshacer(self):
        if not self.hechas:
            return False
        nombre, cerro = self.hechas.pop()
        (self.cerradas.discard if cerro else self.cerradas.add)(nombre)
        self.deshechas.append((nombre, cerro))
        return True

    def rehacer(self):
        if not self.deshechas:
            return False
        nombre, cerro = self.deshechas.pop()
        (self.cerradas.add if cerro else self.cerradas.discard)(nombre)
        self.hechas.append((nombre, cerro))
        return True


class PruebasMedidor(unittest.TestCase):

    def test_cronometrar_separa_preparacion(self):
        preparaciones = []

        def preparar(n, _contexto):
            preparaciones.append(n)
            return list(range(n))

        escenario = medidor.Escenario("suma", "Rx", "elementos", preparar, sum)
        mediana, muestras, salida = medidor.cronometrar(escenario, 100, 4, None)
        self.assertEqual(len(muestras), 4)
        self.assertGreater(mediana, 0)
        self.assertIsNone(salida)
        self.assertEqual(preparaciones, [100])

    def test_restaurar_fuera_del_tiempo_en_cada_repeticion(self):
        eventos = []
        escenario = medidor.Escenario(
            "cambiar", "Rx", "elementos", lambda n, c: [0],
            lambda estado: eventos.append("op"),
            restaurar=lambda estado: eventos.append("restaurar"))
        medidor.cronometrar(escenario, 1, 3, None, calentamiento=1)
        self.assertEqual(eventos, ["op", "restaurar"] * 4)

    def test_pendientes_si_falta_el_modulo(self):
        original = medidor._disponibles
        medidor._disponibles = lambda: []
        try:
            filas = medidor.medir([10], repeticiones=1)
        finally:
            medidor._disponibles = original
        self.assertTrue(filas)
        for fila in filas:
            self.assertTrue(fila["estado"].startswith("pendiente"))

    def test_r10_relacion_entre_tamanos(self):
        if "fila" not in medidor._disponibles():
            self.skipTest("motor/fila.py no esta disponible")
        filas = medidor.medir([2000, 4000], repeticiones=3, solo="R10")
        medidas = [f for f in filas if f["estado"] == "medido"]
        self.assertEqual(len(medidas), 4)
        self.assertIsNone(medidas[0]["relacion"])
        self.assertIsNotNone(medidas[1]["relacion"])
        self.assertEqual(medidas[0]["tamano_salida"], 2000)
        self.assertEqual(medidas[0]["esperado"], "O(n)")

    def test_todos_los_escenarios_de_red_con_red_falsa(self):
        disponibles, crear = medidor._disponibles, medidor._crear_red
        medidor._disponibles = lambda: ["fila", "red"]
        medidor._crear_red = RedFalsa
        try:
            filas = medidor.medir([200, 400], repeticiones=2)
        finally:
            medidor._disponibles, medidor._crear_red = disponibles, crear
        estados = {f["estado"] for f in filas}
        self.assertEqual(estados, {"medido"}, [f for f in filas if f["estado"] != "medido"])
        requisitos = {f["requisito"] for f in filas}
        self.assertEqual(requisitos, {"carga", "R1", "R2", "R3", "R4", "R5", "R6",
                                      "R7", "R8", "R9", "R10"})
        operaciones = {f["operacion"] for f in filas}
        for nombre in ("agregar_parada", "quitar_parada", "cerrar", "reabrir",
                       "deshacer un cierre", "rehacer un cierre", "recorrido al reves"):
            self.assertIn(nombre, operaciones)

    def test_restaurar_deja_la_red_igual(self):
        disponibles, crear = medidor._disponibles, medidor._crear_red
        medidor._disponibles = lambda: ["red"]
        redes = []
        medidor._crear_red = lambda carpeta: redes.append(RedFalsa(carpeta)) or redes[-1]
        try:
            for requisito in ("R7", "R8", "R9"):
                medidor.medir([100], repeticiones=3, solo=requisito)
        finally:
            medidor._disponibles, medidor._crear_red = disponibles, crear
        for red in redes:
            self.assertEqual(red.cerradas, set())
            self.assertEqual(len(red.recorrido("R0001")), 20)

    def test_medir_api_valida_limites(self):
        for tamanos, repeticiones in [([], 3), ([0], 3), ([10**6], 3), ("100", 3),
                                      ([100] * 6, 3), ([100], 0), ([100], 10),
                                      ([True], 3), ([100], 2.5)]:
            with self.subTest(tamanos=tamanos, repeticiones=repeticiones):
                with self.assertRaises(ValueError):
                    medidor.medir_api(tamanos, repeticiones)

    def test_medir_api_devuelve_json(self):
        import json
        filas = medidor.medir_api([500], 1)
        self.assertEqual(json.loads(json.dumps(filas)), filas)


if __name__ == "__main__":
    unittest.main()
