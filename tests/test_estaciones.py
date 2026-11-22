import unittest

from motor.estaciones import IndiceEstaciones

def _crear():
    return IndiceEstaciones(
        ["Calle 80", "Calle 100", "Américas", "Calle 72"]
    )


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

    # ---------- R2: autocompletar ----------
    def test_autocompletar_alfabetico_y_con_nombre_original(self):
        indice = _crear()
        self.assertEqual(
            indice.autocompletar("calle", 10),
            ["Calle 100", "Calle 72", "Calle 80"],
        )

    def test_autocompletar_respeta_k(self):
        indice = _crear()
        self.assertEqual(
            indice.autocompletar("calle", 2), ["Calle 100", "Calle 72"]
        )
        self.assertEqual(indice.autocompletar("calle", 1), ["Calle 100"])

    def test_autocompletar_prefijo_vacio_da_las_primeras_k(self):
        indice = _crear()
        self.assertEqual(
            indice.autocompletar("", 3), ["Américas", "Calle 100", "Calle 72"]
        )

    def test_autocompletar_sin_coincidencias(self):
        indice = _crear()
        self.assertEqual(indice.autocompletar("zzz", 5), [])

    def test_autocompletar_ignora_tildes_y_mayusculas(self):
        indice = _crear()
        self.assertEqual(indice.autocompletar("AMÉRICA", 5), ["Américas"])

    def test_autocompletar_omite_cerradas_y_las_recupera(self):
        indice = _crear()
        indice.cambiar_estado("Calle 72", False)
        self.assertEqual(
            indice.autocompletar("calle", 10), ["Calle 100", "Calle 80"]
        )
        indice.cambiar_estado("Calle 72", True)
        self.assertEqual(
            indice.autocompletar("calle", 10),
            ["Calle 100", "Calle 72", "Calle 80"],
        )

    def test_autocompletar_k_cero_o_negativo(self):
        indice = _crear()
        self.assertEqual(indice.autocompletar("calle", 0), [])
        self.assertEqual(indice.autocompletar("calle", -3), [])

    def test_autocompletar_tipos_invalidos(self):
        indice = _crear()
        with self.assertRaises(TypeError):
            indice.autocompletar("calle", True)
        with self.assertRaises(TypeError):
            indice.autocompletar("calle", "3")
        with self.assertRaises(TypeError):
            indice.autocompletar("calle", 2.5)
        with self.assertRaises(TypeError):
            indice.autocompletar(5, 3)

    def test_autocompletar_red_vacia(self):
        self.assertEqual(IndiceEstaciones([]).autocompletar("a", 5), [])

if __name__ == "__main__":
    unittest.main()