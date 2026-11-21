"""Pruebas de R7: rutas como lista doblemente enlazada.

Cada mutacion se comprueba en ida Y vuelta, y contra los invariantes de
enlaces, para detectar nodos perdidos o ciclos.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apoyo

apoyo.preparar_motor()

from motor.rutas import AlmacenRutas, Ruta
from motor.tabla_hash import TablaHash


def invertida(lista):
    return lista[::-1]


class InvariantesMixin:
    def comprobar(self, ruta, esperado):
        """Ida, vuelta, extremos, cantidad y enlaces coherentes."""
        self.assertEqual(ruta.recorrido(), esperado)
        self.assertEqual(ruta.recorrido(al_reves=True), invertida(esperado))
        self.assertEqual(len(ruta), len(esperado))
        if not esperado:
            self.assertIsNone(ruta.primera())
            self.assertIsNone(ruta.ultima())
            return
        self.assertEqual(ruta.primera().estacion, esperado[0])
        self.assertEqual(ruta.ultima().estacion, esperado[-1])
        self.assertIsNone(ruta.primera().anterior)
        self.assertIsNone(ruta.ultima().siguiente)
        nodo = ruta.primera()
        pasos = 0
        while nodo.siguiente is not None:
            self.assertIs(nodo.siguiente.anterior, nodo)
            nodo = nodo.siguiente
            pasos += 1
            self.assertLess(pasos, len(esperado), "hay un ciclo")
        self.assertIs(nodo, ruta.ultima())
        for nombre in esperado:
            self.assertEqual(ruta.nodo(nombre).estacion, nombre)


class RutaBase(InvariantesMixin):
    """Las mismas pruebas corren con y sin indice por nombre."""

    fabrica = None

    def nueva(self, *paradas):
        ruta = Ruta("R1", self.fabrica)
        for parada in paradas:
            self.assertTrue(ruta.agregar_al_final(parada))
        return ruta

    def test_ruta_vacia(self):
        ruta = self.nueva()
        self.comprobar(ruta, [])
        self.assertFalse(ruta.contiene("A"))
        self.assertFalse(ruta.quitar("A"))
        self.assertFalse(ruta.insertar_despues("B", "A"))
        self.assertIsNone(ruta.anterior_de("A"))

    def test_recorrido_en_ambos_sentidos(self):
        self.comprobar(self.nueva("A", "B", "C"), ["A", "B", "C"])

    def test_recorrido_devuelve_copia(self):
        ruta = self.nueva("A", "B")
        ruta.recorrido().append("X")
        self.comprobar(ruta, ["A", "B"])

    def test_insertar_en_medio(self):
        ruta = self.nueva("A", "C")
        self.assertTrue(ruta.insertar_despues("B", "A"))
        self.comprobar(ruta, ["A", "B", "C"])

    def test_insertar_despues_de_la_cola(self):
        ruta = self.nueva("A", "B")
        self.assertTrue(ruta.insertar_despues("C", "B"))
        self.comprobar(ruta, ["A", "B", "C"])

    def test_insertar_con_una_sola_parada(self):
        ruta = self.nueva("A")
        self.assertTrue(ruta.insertar_despues("B", "A"))
        self.comprobar(ruta, ["A", "B"])

    def test_insertar_al_inicio(self):
        ruta = self.nueva("B", "C")
        self.assertTrue(ruta.insertar_al_inicio("A"))
        self.comprobar(ruta, ["A", "B", "C"])
        vacia = self.nueva()
        self.assertTrue(vacia.insertar_al_inicio("A"))
        self.comprobar(vacia, ["A"])

    def test_no_repite_estaciones(self):
        ruta = self.nueva("A", "B")
        self.assertFalse(ruta.insertar_despues("A", "B"))
        self.assertFalse(ruta.agregar_al_final("B"))
        self.assertFalse(ruta.insertar_al_inicio("B"))
        self.comprobar(ruta, ["A", "B"])

    def test_referencia_ausente_no_cambia_nada(self):
        ruta = self.nueva("A", "B")
        self.assertFalse(ruta.insertar_despues("C", "Z"))
        self.comprobar(ruta, ["A", "B"])
        self.assertFalse(ruta.contiene("C"))

    def test_quitar_cabeza_medio_y_cola(self):
        ruta = self.nueva("A", "B", "C", "D")
        self.assertTrue(ruta.quitar("A"))
        self.comprobar(ruta, ["B", "C", "D"])
        self.assertTrue(ruta.quitar("C"))
        self.comprobar(ruta, ["B", "D"])
        self.assertTrue(ruta.quitar("D"))
        self.comprobar(ruta, ["B"])

    def test_quitar_la_unica_deja_ruta_vacia_y_reutilizable(self):
        ruta = self.nueva("A")
        self.assertTrue(ruta.quitar("A"))
        self.comprobar(ruta, [])
        self.assertTrue(ruta.agregar_al_final("B"))
        self.comprobar(ruta, ["B"])

    def test_quitar_ausente(self):
        ruta = self.nueva("A", "B")
        self.assertFalse(ruta.quitar("Z"))
        self.comprobar(ruta, ["A", "B"])

    def test_quitar_y_volver_a_insertar(self):
        ruta = self.nueva("A", "B", "C")
        self.assertEqual(ruta.anterior_de("B"), "A")
        self.assertTrue(ruta.quitar("B"))
        self.assertFalse(ruta.contiene("B"))
        self.assertTrue(ruta.insertar_despues("B", "A"))
        self.comprobar(ruta, ["A", "B", "C"])

    def test_anterior_de(self):
        ruta = self.nueva("A", "B", "C")
        self.assertIsNone(ruta.anterior_de("A"))
        self.assertEqual(ruta.anterior_de("C"), "B")
        self.assertIsNone(ruta.anterior_de("Z"))

    def test_secuencia_larga_mantiene_enlaces(self):
        ruta = self.nueva("E0")
        esperado = ["E0"]
        for i in range(1, 200):
            referencia = esperado[(i * 7) % len(esperado)]
            self.assertTrue(ruta.insertar_despues("E%d" % i, referencia))
            esperado.insert(esperado.index(referencia) + 1, "E%d" % i)
        for i in range(0, 200, 3):
            self.assertTrue(ruta.quitar("E%d" % i))
            esperado.remove("E%d" % i)
        self.comprobar(ruta, esperado)


class RutaSinIndiceTests(RutaBase, unittest.TestCase):
    fabrica = None


class RutaConTablaHashTests(RutaBase, unittest.TestCase):
    fabrica = TablaHash


class AlmacenBase(InvariantesMixin):
    fabrica = None

    def almacen(self):
        almacen = AlmacenRutas(self.fabrica)
        for parada in ["A", "B", "C"]:
            almacen.agregar_al_final("R1", parada)
        for parada in ["C", "D"]:
            almacen.agregar_al_final("R2", parada)
        return almacen

    def test_recorrido_publico(self):
        almacen = self.almacen()
        self.assertEqual(almacen.recorrido("R1"), ["A", "B", "C"])
        self.assertEqual(almacen.recorrido("R1", True), ["C", "B", "A"])
        self.assertEqual(almacen.recorrido("NO"), [])
        self.assertEqual(almacen.nombres(), ["R1", "R2"])
        self.assertEqual(len(almacen), 2)

    def test_agregar_y_quitar_actualizan_pertenencia(self):
        almacen = self.almacen()
        self.assertEqual(sorted(almacen.rutas_de("C")), ["R1", "R2"])
        self.assertEqual(almacen.rutas_de("D"), ["R2"])
        self.assertTrue(almacen.agregar_parada("R1", "D", "C"))
        # El orden de rutas_de no es parte del acuerdo; se compara ordenado.
        self.assertEqual(sorted(almacen.rutas_de("D")), ["R1", "R2"])
        self.assertTrue(almacen.quitar_parada("R2", "D"))
        self.assertEqual(almacen.rutas_de("D"), ["R1"])
        self.assertTrue(almacen.quitar_parada("R1", "D"))
        self.assertEqual(almacen.rutas_de("D"), [])
        self.comprobar(almacen.obtener("R1"), ["A", "B", "C"])
        self.comprobar(almacen.obtener("R2"), ["C"])

    def test_operaciones_que_no_cambian(self):
        almacen = self.almacen()
        self.assertFalse(almacen.agregar_parada("NO", "X", "A"))
        self.assertFalse(almacen.agregar_parada("R1", "B", "A"))
        self.assertFalse(almacen.agregar_parada("R1", "X", "Z"))
        self.assertFalse(almacen.quitar_parada("NO", "A"))
        self.assertFalse(almacen.quitar_parada("R1", "D"))
        self.assertFalse(almacen.insertar_al_inicio("NO", "X"))
        self.assertEqual(almacen.rutas_de("X"), [])
        self.assertIsNone(almacen.obtener("NO"))
        self.assertEqual(len(almacen), 2)

    def test_ruta_queda_vacia_y_sigue_existiendo(self):
        almacen = self.almacen()
        self.assertTrue(almacen.quitar_parada("R2", "C"))
        self.assertTrue(almacen.quitar_parada("R2", "D"))
        self.assertEqual(almacen.recorrido("R2"), [])
        self.assertIsNotNone(almacen.obtener("R2"))
        self.assertFalse(almacen.agregar_parada("R2", "C", "D"))
        self.assertTrue(almacen.insertar_al_inicio("R2", "C"))
        self.assertEqual(sorted(almacen.rutas_de("C")), ["R1", "R2"])

    def test_rutas_de_devuelve_copia(self):
        almacen = self.almacen()
        almacen.rutas_de("C").append("X")
        self.assertEqual(sorted(almacen.rutas_de("C")), ["R1", "R2"])


class AlmacenSinIndiceTests(AlmacenBase, unittest.TestCase):
    fabrica = None


class AlmacenConTablaHashTests(AlmacenBase, unittest.TestCase):
    fabrica = TablaHash


if __name__ == "__main__":
    unittest.main()
