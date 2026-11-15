import unittest

from motor.tabla_hash import TablaHash


class ClaveConColision:
    """Clave de prueba que obliga a varias entradas a compartir cubeta."""

    def __init__(self, valor):
        self.valor = valor

    def __hash__(self):
        return 7

    def __eq__(self, otra):
        return (
            isinstance(otra, ClaveConColision)
            and self.valor == otra.valor
        )


class TablaHashTests(unittest.TestCase):
    def test_tabla_vacia_y_clave_ausente(self):
        tabla = TablaHash()
        self.assertEqual(list(tabla.pares()), [])
        self.assertIsNone(tabla.obtener("ausente"))
        self.assertEqual(tabla.obtener("ausente", "alternativa"), "alternativa")
        self.assertFalse(tabla.eliminar("ausente"))

    def test_inserta_y_obtiene(self):
        tabla = TablaHash()
        tabla.guardar("estacion", "Museo")
        self.assertEqual(tabla.obtener("estacion"), "Museo")

    def test_reemplaza_sin_duplicar_el_par(self):
        tabla = TablaHash()
        tabla.guardar("ruta", "A")
        tabla.guardar("ruta", "B")
        self.assertEqual(tabla.obtener("ruta"), "B")
        self.assertEqual(list(tabla.pares()), [("ruta", "B")])

    def test_valor_none_no_se_confunde_con_clave_ausente(self):
        tabla = TablaHash()
        tabla.guardar("valor", None)
        marcador = object()
        self.assertIsNone(tabla.obtener("valor", marcador))
        self.assertIs(tabla.obtener("ausente", marcador), marcador)

    def test_resuelve_colisiones_y_elimina_cada_posicion(self):
        tabla = TablaHash()
        claves = [
            ClaveConColision("primera"),
            ClaveConColision("segunda"),
            ClaveConColision("tercera"),
        ]
        for clave in claves:
            tabla.guardar(clave, clave.valor)

        self.assertEqual(tabla.obtener(ClaveConColision("segunda")), "segunda")
        self.assertTrue(tabla.eliminar(ClaveConColision("segunda")))
        self.assertIsNone(tabla.obtener(ClaveConColision("segunda")))
        self.assertEqual(tabla.obtener(claves[0]), "primera")
        self.assertEqual(tabla.obtener(claves[2]), "tercera")
        self.assertTrue(tabla.eliminar(claves[0]))
        self.assertTrue(tabla.eliminar(claves[2]))
        self.assertFalse(tabla.eliminar(claves[2]))

    def test_crece_y_conserva_los_elementos(self):
        tabla = TablaHash()
        capacidad_inicial = len(tabla._cubetas)

        for numero in range(100):
            tabla.guardar(numero, str(numero))

        self.assertGreater(len(tabla._cubetas), capacidad_inicial)
        for numero in range(100):
            self.assertEqual(tabla.obtener(numero), str(numero))

    def test_colisiones_tambien_sobreviven_redimensionamiento(self):
        tabla = TablaHash()
        claves = [ClaveConColision(numero) for numero in range(40)]

        for clave in claves:
            tabla.guardar(clave, clave.valor)

        for clave in claves:
            self.assertEqual(tabla.obtener(clave), clave.valor)

        for clave in claves[::2]:
            self.assertTrue(tabla.eliminar(clave))

        for clave in claves[1::2]:
            self.assertEqual(tabla.obtener(clave), clave.valor)

    def test_muchas_claves_y_pares(self):
        tabla = TablaHash()
        esperado = {}

        for numero in range(250):
            valor = numero * 3
            tabla.guardar(numero, valor)
            esperado[numero] = valor

        self.assertEqual(dict(tabla.pares()), esperado)

        for numero in range(0, 250, 2):
            self.assertTrue(tabla.eliminar(numero))
            del esperado[numero]

        self.assertEqual(dict(tabla.pares()), esperado)

    def test_rechaza_clave_no_hashable(self):
        tabla = TablaHash()
        with self.assertRaises(TypeError):
            tabla.guardar([], "valor")
        with self.assertRaises(TypeError):
            tabla.obtener([])
        with self.assertRaises(TypeError):
            tabla.eliminar([])
            
    def test_reemplazo(self):
        tabla = TablaHash()
        tabla.guardar("clave", "valor1")
        tabla.guardar("clave", "valor2")
        self.assertEqual(tabla.obtener("clave"), "valor2")
        self.assertEqual(list(tabla.pares()), [("clave", "valor2")])
        self.assertEqual(tabla._cantidad, 1)



    def test_eliminacion(self):
        tabla = TablaHash()
        tabla.guardar("clave", "valor")
        self.assertTrue(tabla.eliminar("clave"))
        self.assertIsNone(tabla.obtener("clave"))
        self.assertFalse(tabla.eliminar("clave"))
        self.assertEqual(tabla._cantidad, 0)
        
        
if __name__ == "__main__":
    unittest.main()