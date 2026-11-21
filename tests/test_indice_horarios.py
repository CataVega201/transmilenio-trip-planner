import unittest
from motor.horarios import IndiceHorarios


class TablaDePrueba(dict):
    obtener = dict.get
    guardar = dict.__setitem__


class IndiceTests(unittest.TestCase):
    def test_parejas_independientes_y_duplicados(self):
        filas = [["B", "X", "25:10"], ["A", "X", "10:00"], ["B", "X", "07:00"],
                 ["B", "Y", "06:15"], ["B", "X", "07:00"]]
        indice = IndiceHorarios(iter(filas), crear_tabla=TablaDePrueba)
        self.assertEqual(indice.cantidad("X", "B"), 3)
        self.assertEqual(indice.siguiente("X", "B", "07:00"), "07:00")
        self.assertEqual(indice.siguiente("X", "B", "07:01"), "25:10")
        self.assertIsNone(indice.siguiente("Y", "B", "07:00"))
        self.assertIsNone(indice.siguiente("X", "C", "00:00"))
        self.assertEqual(indice.cantidad("Z", "B"), 0)
        with self.assertRaises(ValueError):
            indice.siguiente("Z", "B", "25:70")

