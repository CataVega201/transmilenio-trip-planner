"""Regresiones de los índices dinámicos y del ranking de la red."""
import math
import random
import unittest

from motor.arbol_ordenado import ArbolOrdenado
from motor.estaciones import IndiceEstaciones
from motor.ranking import IndiceRanking


class ArbolTests(unittest.TestCase):
    def test_actualizaciones_aleatorias_y_cotas_de_altura(self):
        azar = random.Random(70)
        arbol = ArbolOrdenado()
        esperado = {}
        for paso in range(2000):
            clave = azar.randrange(300)
            if azar.randrange(3):
                esperado[clave] = paso
                arbol.guardar(clave, paso)
            else:
                esperado.pop(clave, None)
                arbol.eliminar(clave)
            self.assertEqual(list(arbol.iterar()), sorted(esperado.items()))
            if arbol._raiz:
                self.assertLessEqual(arbol._raiz.altura, 2 * math.log2(len(esperado) + 2))
            self.assertEqual(list(arbol.iterar(80, 130)),
                             [(k, v) for k, v in sorted(esperado.items()) if 80 <= k <= 130])

    def test_orden_secuencial_no_degenera_y_elimina_todo(self):
        arbol = ArbolOrdenado()
        for i in range(5000):
            arbol.guardar(i, i)
        self.assertLess(arbol._raiz.altura, 25)
        for i in range(5000):
            arbol.eliminar(i)
        self.assertEqual(list(arbol.iterar()), [])
        self.assertIsNone(arbol._raiz)


class IndicesTests(unittest.TestCase):
    def test_rangos_limites_y_reaperturas(self):
        indice = IndiceEstaciones(["Zeta", "Álfa", "Bravo", "Ñandú"])
        self.assertEqual(indice.rango(" alfa ", "bravo"), ["Álfa", "Bravo"])
        self.assertEqual(indice.rango("Z", "A"), [])
        indice.cambiar_estado("alfa", False)
        self.assertEqual(indice.rango("A", "B"), [])
        self.assertEqual(indice.autocompletar("", 2), ["Bravo", "Zeta"])
        indice.cambiar_estado("alfa", True)
        self.assertEqual(indice.autocompletar("Á", 1), ["Álfa"])
        for a, b in [(None, "Z"), ("A", 5)]:
            with self.assertRaises(TypeError):
                indice.rango(a, b)

    def test_cerradas_no_agotan_la_busqueda(self):
        indice = IndiceEstaciones([f"A{i:05d}" for i in range(1000)])
        for i in range(999):
            indice.cambiar_estado(f"A{i:05d}", False)
        self.assertEqual(indice.autocompletar("A", 5), ["A00999"])
        self.assertEqual(indice.rango("A00000", "A00999"), ["A00999"])

    def test_ranking_actualizacion_incremental_comparada_con_referencia(self):
        azar = random.Random(6)
        nombres = [f"Estación {i:03d}" for i in range(100)]
        indice = IndiceRanking([(n, 0) for n in nombres])
        estado = {n: (0, True) for n in nombres}
        for paso in range(1000):
            nombre = azar.choice(nombres)
            cuenta, abierta = azar.randrange(50), bool(azar.randrange(2))
            estado[nombre] = (cuenta, abierta)
            indice.actualizar_estacion(nombre, cuenta, abierta)
            esperado = sorted([(n, c) for n, (c, a) in estado.items() if a],
                              key=lambda par: (-par[1], par[0]))
            k = azar.randrange(120)
            self.assertEqual(indice.ranking(k), esperado[:k])
        for valor in [True, 2.5, None]:
            with self.assertRaises(TypeError):
                indice.ranking(valor)
        self.assertEqual(indice.ranking(-1), [])


class RedCompletaTests(unittest.TestCase):
    def test_secuencias_de_edicion_cierres_e_historial(self):
        import csv
        import tempfile
        from pathlib import Path
        from motor import Red
        with tempfile.TemporaryDirectory() as carpeta:
            for archivo, cabecera, filas in [
                ("estaciones.csv", ["nombre"], [("Álfa",), ("Bravo",), ("Cambio",)]),
                ("rutas.csv", ["ruta", "orden", "estacion"],
                 [("R", 1, "Álfa"), ("R", 2, "Bravo"), ("R", 3, "Cambio")]),
                ("horarios.csv", ["ruta", "estacion", "hora"],
                 [("R", "Bravo", "05:00"), ("R", "Bravo", "05:00")]),
            ]:
                with (Path(carpeta) / archivo).open("w", encoding="utf-8", newline="") as f:
                    w = csv.writer(f)
                    w.writerow(cabecera)
                    w.writerows(filas)
            red = Red(carpeta)
            base = red.ranking(10)
            self.assertEqual(base[0], ("Bravo", 2))
            self.assertTrue(red.cerrar("Bravo"))
            self.assertTrue(red.quitar_parada("R", "Bravo"))
            self.assertNotIn("Bravo", red.autocompletar("", 10))
            self.assertTrue(red.deshacer())
            self.assertNotIn(("Bravo", 2), red.ranking(10))
            self.assertTrue(red.deshacer())
            self.assertEqual(red.ranking(10), base)
            self.assertEqual(red.rango("alfa", "cambio"), ["Álfa", "Bravo", "Cambio"])
            self.assertTrue(red.rehacer())
            self.assertTrue(red.rehacer())
            self.assertTrue(red.reabrir("Bravo"))
            self.assertIn(("Bravo", 0), red.ranking(10))
            self.assertTrue(red.agregar_parada("R", "Bravo", "Álfa"))
            self.assertEqual(red.ranking(1), [("Bravo", 2)])
