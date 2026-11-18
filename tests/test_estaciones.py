import unittest

from motor.estaciones import IndiceEstaciones


class IndiceEstacionesTests(unittest.TestCase):
    def test_estado_abierta_y_ausente(self):
        indice = IndiceEstaciones(["Portal Norte", "Américas"])
        self.assertEqual(indice.estado("portal norte"), "ABIERTA")
        self.assertEqual(indice.estado("AMÉRICAS"), "ABIERTA")
        self.assertEqual(indice.estado("Calle 100"), "NO EXISTE")

    def test_cerrar_y_reabrir(self):
        indice = IndiceEstaciones(["Portal Norte"])
        self.assertTrue(indice.cambiar_estado("portal norte", False))
        self.assertEqual(indice.estado("Portal Norte"), "CERRADA")
        self.assertFalse(indice.cambiar_estado("Portal Norte", False))
        self.assertTrue(indice.cambiar_estado("Portal Norte", True))
        self.assertEqual(indice.estado("Portal Norte"), "ABIERTA")
        self.assertFalse(indice.cambiar_estado("Calle 100", False))
        
    def test_cerrada_no_es_ausente(self):
        indice = IndiceEstaciones(["Suba"])
        indice.cambiar_estado("Suba", False)
        self.assertEqual(indice.estado("Suba"), "CERRADA")
        self.assertEqual(indice.estado("Calle 100"), "NO EXISTE")


if __name__ == "__main__":
    unittest.main()