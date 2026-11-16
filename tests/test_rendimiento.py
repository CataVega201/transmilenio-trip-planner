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


class PruebasMedidor(unittest.TestCase):

    def test_cronometrar_separa_preparacion(self):
        preparaciones = []

        def preparar(n, _carpeta):
            preparaciones.append(n)
            return list(range(n))

        escenario = medidor.Escenario("suma", "Rx", "elementos", preparar, sum)
        mediana, muestras, salida = medidor.cronometrar(escenario, 100, 4, None)
        self.assertEqual(len(muestras), 4)
        self.assertGreater(mediana, 0)
        self.assertIsNone(salida)          # sum no devuelve una lista
        self.assertEqual(preparaciones, [100])  # no mutable: se prepara una vez

    def test_mutable_se_prepara_en_cada_repeticion(self):
        preparaciones = []

        def preparar(n, _carpeta):
            preparaciones.append(n)
            return [0] * n

        escenario = medidor.Escenario("vaciar", "Rx", "elementos", preparar,
                                      lambda lista: lista.clear(), mutable=True)
        medidor.cronometrar(escenario, 10, 3, None, calentamiento=1)
        # 1 inicial + 1 tras calentar + 3 repeticiones
        self.assertEqual(len(preparaciones), 5)

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

    def test_relacion_entre_tamanos(self):
        if "fila" not in medidor._disponibles():
            self.skipTest("motor/fila.py aun no esta integrado en esta rama")
        filas = medidor.medir([2000, 4000], repeticiones=3, solo="R10")
        medidas = [f for f in filas if f["estado"] == "medido"]
        self.assertEqual(len(medidas), 4)
        self.assertIsNone(medidas[0]["relacion"])
        self.assertIsNotNone(medidas[1]["relacion"])
        self.assertEqual(medidas[0]["tamano_salida"], 2000)


if __name__ == "__main__":
    unittest.main()
