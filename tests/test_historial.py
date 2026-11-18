"""Pruebas de R9: pilas propias e historial de deshacer/rehacer.

Aqui las acciones son registros pequenos de ejemplo sobre un contador. La
integracion con cierres y rutas reales se prueba en tests/test_red.py.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apoyo

apoyo.preparar_motor()

from motor.historial import Historial, Pila


class PilaTests(unittest.TestCase):
    def test_vacia(self):
        pila = Pila()
        self.assertTrue(pila.vacia())
        self.assertEqual(len(pila), 0)
        self.assertIsNone(pila.desapilar())
        self.assertIsNone(pila.cima())

    def test_orden_lifo(self):
        pila = Pila()
        for valor in [1, 2, 3]:
            pila.apilar(valor)
        self.assertEqual(len(pila), 3)
        self.assertEqual(pila.cima(), 3)
        self.assertEqual([pila.desapilar() for _ in range(3)], [3, 2, 1])
        self.assertTrue(pila.vacia())

    def test_vaciar_y_reutilizar(self):
        pila = Pila()
        pila.apilar("a")
        pila.apilar("b")
        pila.vaciar()
        self.assertTrue(pila.vacia())
        self.assertEqual(len(pila), 0)
        pila.apilar("c")
        self.assertEqual(pila.desapilar(), "c")

    def test_muchos_elementos_sin_recursion(self):
        pila = Pila()
        for valor in range(200000):
            pila.apilar(valor)
        pila.vaciar()
        self.assertTrue(pila.vacia())


class Contador:
    """Sistema de ejemplo: cada accion es [anterior, nuevo]."""

    def __init__(self):
        self.valor = 0
        self.historial = Historial()

    def cambiar(self, nuevo):
        if nuevo == self.valor:
            return False  # sin efecto: no se registra
        self.historial.registrar([self.valor, nuevo])
        self.valor = nuevo
        return True

    def deshacer(self):
        accion = self.historial.deshacer()
        if accion is None:
            return False
        self.valor = accion[0]
        return True

    def rehacer(self):
        accion = self.historial.rehacer()
        if accion is None:
            return False
        self.valor = accion[1]
        return True


class HistorialTests(unittest.TestCase):
    def test_historial_vacio(self):
        historial = Historial()
        self.assertIsNone(historial.deshacer())
        self.assertIsNone(historial.rehacer())
        self.assertFalse(historial.puede_deshacer())
        self.assertFalse(historial.puede_rehacer())
        self.assertEqual(historial.pendientes(), [0, 0])

    def test_deshacer_en_orden_inverso(self):
        c = Contador()
        for valor in [1, 2, 3]:
            c.cambiar(valor)
        self.assertTrue(c.deshacer())
        self.assertEqual(c.valor, 2)
        self.assertTrue(c.deshacer())
        self.assertEqual(c.valor, 1)
        self.assertTrue(c.deshacer())
        self.assertEqual(c.valor, 0)
        self.assertFalse(c.deshacer())
        self.assertEqual(c.valor, 0)

    def test_rehacer_reaplica_en_orden(self):
        c = Contador()
        for valor in [1, 2, 3]:
            c.cambiar(valor)
        c.deshacer()
        c.deshacer()
        self.assertTrue(c.rehacer())
        self.assertEqual(c.valor, 2)
        self.assertTrue(c.rehacer())
        self.assertEqual(c.valor, 3)
        self.assertFalse(c.rehacer())
        self.assertEqual(c.valor, 3)

    def test_cambio_nuevo_vacia_rehacer(self):
        c = Contador()
        c.cambiar(1)
        c.cambiar(2)
        c.deshacer()
        self.assertTrue(c.historial.puede_rehacer())
        c.cambiar(9)
        self.assertFalse(c.historial.puede_rehacer())
        self.assertFalse(c.rehacer())
        self.assertEqual(c.valor, 9)
        c.deshacer()
        self.assertEqual(c.valor, 1)
        c.deshacer()
        self.assertEqual(c.valor, 0)

    def test_accion_sin_efecto_no_registra_ni_vacia_rehacer(self):
        c = Contador()
        c.cambiar(1)
        c.deshacer()
        self.assertFalse(c.cambiar(0))
        self.assertEqual(c.historial.pendientes(), [0, 1])
        self.assertTrue(c.rehacer())
        self.assertEqual(c.valor, 1)

    def test_deshacer_y_rehacer_no_crean_acciones(self):
        c = Contador()
        c.cambiar(1)
        c.cambiar(2)
        for _ in range(5):
            c.deshacer()
            c.rehacer()
        self.assertEqual(c.historial.pendientes(), [2, 0])
        c.deshacer()
        c.deshacer()
        self.assertEqual(c.historial.pendientes(), [0, 2])
        self.assertEqual(c.valor, 0)

    def test_devuelve_la_misma_accion_registrada(self):
        historial = Historial()
        accion = ["CERRAR", "A"]
        historial.registrar(accion)
        self.assertIs(historial.deshacer(), accion)
        self.assertIs(historial.rehacer(), accion)

    def test_secuencia_larga_alternada(self):
        c = Contador()
        for valor in range(1, 1001):
            c.cambiar(valor)
        for _ in range(400):
            c.deshacer()
        self.assertEqual(c.valor, 600)
        for _ in range(150):
            c.rehacer()
        self.assertEqual(c.valor, 750)
        self.assertEqual(c.historial.pendientes(), [750, 250])


if __name__ == "__main__":
    unittest.main()
