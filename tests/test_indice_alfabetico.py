import unittest

from motor.indice_alfabetico import _ordenar, _primer_indice


class OrdenarTests(unittest.TestCase):
    def test_ordena_numeros(self):
        self.assertEqual(_ordenar([5, 2, 9, 1, 7, 3]), [1, 2, 3, 5, 7, 9])

    def test_lista_vacia_y_de_un_elemento(self):
        self.assertEqual(_ordenar([]), [])
        self.assertEqual(_ordenar([4]), [4])

    def test_conserva_repetidos(self):
        self.assertEqual(_ordenar([3, 3, 1, 3]), [1, 3, 3, 3])

    def test_ordena_textos(self):
        nombres = ["SUBA", "CALLE 100", "PORTAL NORTE", "AMERICAS"]
        self.assertEqual(
            _ordenar(nombres),
            ["AMERICAS", "CALLE 100", "PORTAL NORTE", "SUBA"],
        )

    def test_no_modifica_la_lista_original(self):
        original = [3, 1, 2]
        _ordenar(original)
        self.assertEqual(original, [3, 1, 2])

    def test_ya_ordenada_e_invertida(self):
        self.assertEqual(_ordenar([1, 2, 3, 4]), [1, 2, 3, 4])
        self.assertEqual(_ordenar([4, 3, 2, 1]), [1, 2, 3, 4])


class PrimerIndiceTests(unittest.TestCase):
    NOMBRES = ["AMERICAS", "CALLE 100", "CALLE 72", "PORTAL NORTE", "SUBA"]

    def test_prefijo_en_medio(self):
        self.assertEqual(_primer_indice(self.NOMBRES, "CALLE"), 1)
        self.assertEqual(_primer_indice(self.NOMBRES, "PORTAL"), 3)

    def test_prefijo_vacio_da_cero(self):
        self.assertEqual(_primer_indice(self.NOMBRES, ""), 0)

    def test_mayor_que_todos_da_la_longitud(self):
        self.assertEqual(_primer_indice(self.NOMBRES, "ZZZ"), 5)

    def test_lista_vacia(self):
        self.assertEqual(_primer_indice([], "A"), 0)

    def test_elemento_exacto(self):
        self.assertEqual(_primer_indice(self.NOMBRES, "SUBA"), 4)


if __name__ == "__main__":
    unittest.main()