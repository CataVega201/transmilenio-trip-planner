"""Pruebas de R10 - simular_fila (contrato del profesor).

Ejecutar desde la carpeta del proyecto:
    .\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_fila.py" -v
"""

import random
import time
import unittest

from motor.fila import ColaFIFO, simular_fila


def simular_segundo_a_segundo(llegadas, frecuencia, capacidad):
    """Version ingenua de referencia (solo para pruebas, fuera de motor/).

    Ordena con sorted (permitido fuera del motor) y recorre cada segundo
    desde 0 con una lista normal. Lenta, pero facil de comprobar a mano.
    """
    n = len(llegadas)
    orden = sorted(range(n), key=lambda i: llegadas[i])  # estable
    salidas = [None] * n
    fila = []
    i = 0
    segundo = 0
    while i < n or fila:
        while i < n and llegadas[orden[i]] == segundo:
            fila.append(orden[i])
            i += 1
        if segundo > 0 and segundo % frecuencia == 0:
            for persona in fila[:capacidad]:
                salidas[persona] = segundo
            fila = fila[capacidad:]
        segundo += 1
    return salidas


class PruebasCola(unittest.TestCase):

    def test_fifo_con_crecimiento_y_vuelta(self):
        cola = ColaFIFO(2)
        cola.encolar(1)
        cola.encolar(2)
        self.assertEqual(cola.desencolar(), 1)
        for valor in range(3, 10):
            cola.encolar(valor)
        salida = []
        while not cola.vacia():
            salida.append(cola.desencolar())
        self.assertEqual(salida, [2, 3, 4, 5, 6, 7, 8, 9])

    def test_desencolar_vacia(self):
        with self.assertRaises(IndexError):
            ColaFIFO().desencolar()


class PruebasCasosNormales(unittest.TestCase):

    def test_ejemplo_explicado(self):
        # Buses en 10, 20, 30... con cupo 2. Los de 0 y 0 suben en 10.
        # El de 1 queda de tercero y sube en 20 junto con el de 10.
        self.assertEqual(simular_fila([0, 0, 1, 10], 10, 2), [10, 10, 20, 20])

    def test_lista_vacia(self):
        self.assertEqual(simular_fila([], 5, 3), [])

    def test_no_hay_bus_en_cero(self):
        self.assertEqual(simular_fila([0], 7, 1), [7])

    def test_llegada_entre_buses(self):
        self.assertEqual(simular_fila([3], 5, 1), [5])

    def test_llegada_justo_con_el_bus(self):
        self.assertEqual(simular_fila([5, 10], 5, 1), [5, 10])

    def test_personas_simultaneas(self):
        self.assertEqual(simular_fila([4, 4, 4], 5, 3), [5, 5, 5])

    def test_cupo_exacto(self):
        self.assertEqual(simular_fila([0, 0, 0], 10, 3), [10, 10, 10])

    def test_una_mas_que_el_cupo(self):
        self.assertEqual(simular_fila([0, 0, 0, 0], 10, 3), [10, 10, 10, 20])

    def test_varias_salidas_seguidas(self):
        self.assertEqual(simular_fila([0, 0, 0, 0, 0], 3, 2), [3, 3, 6, 6, 9])

    def test_fifo_quien_espera_sube_antes(self):
        # Cupo 1: el segundo de los que llegaron en 0 sube antes que el de 10.
        self.assertEqual(simular_fila([0, 0, 10], 10, 1), [10, 20, 30])

    def test_llegadas_desordenadas_respetan_orden_de_salida(self):
        # El de 3 llego antes que el de 25 aunque aparezca despues en la lista.
        self.assertEqual(simular_fila([25, 3, 3], 10, 1), [30, 10, 20])

    def test_desordenadas_con_cupo_lleno(self):
        # Orden real de llegada: 0 (pos 2), 1 (pos 1), 2 (pos 0). Cupo 2.
        self.assertEqual(simular_fila([2, 1, 0], 5, 2), [10, 5, 5])

    def test_empate_respeta_posicion_en_la_lista(self):
        # Tres llegan en 4 mezclados con otro que llega en 9. Cupo 2:
        # en 5 suben las posiciones 0 y 2; en 10 la posicion 3 y la del 9.
        self.assertEqual(simular_fila([4, 9, 4, 4], 5, 2), [5, 10, 5, 10])

    def test_gran_salto_de_tiempo(self):
        inicio = time.perf_counter()
        resultado = simular_fila([0, 1000000, 1000000000], 7, 1)
        duracion = time.perf_counter() - inicio
        # 1000000 = 7 * 142857 + 1 -> siguiente bus 1000006.
        # 1000000000 = 7 * 142857142 + 6 -> siguiente bus 1000000001.
        self.assertEqual(resultado, [7, 1000006, 1000000001])
        self.assertLess(duracion, 0.1)

    def test_segundos_con_decimales(self):
        self.assertEqual(simular_fila([0.5, 2.5], 2.5, 1), [2.5, 5.0])

    def test_no_modifica_la_entrada(self):
        llegadas = [5, 0, 1]
        simular_fila(llegadas, 2, 1)
        self.assertEqual(llegadas, [5, 0, 1])

    def test_acepta_tupla(self):
        self.assertEqual(simular_fila((0, 1), 1, 1), [1, 2])

    def test_devuelve_lista_simple(self):
        resultado = simular_fila([0, 3], 5, 2)
        self.assertIsInstance(resultado, list)
        for valor in resultado:
            self.assertIsInstance(valor, int)


class PruebasEntradasInvalidas(unittest.TestCase):

    def test_frecuencia_cero_o_negativa(self):
        with self.assertRaises(ValueError):
            simular_fila([0], 0, 1)
        with self.assertRaises(ValueError):
            simular_fila([0], -5, 1)

    def test_capacidad_cero_o_negativa(self):
        with self.assertRaises(ValueError):
            simular_fila([0], 5, 0)
        with self.assertRaises(ValueError):
            simular_fila([0], 5, -1)

    def test_llegada_negativa(self):
        with self.assertRaises(ValueError):
            simular_fila([-1, 0], 5, 1)

    def test_tipos_incompatibles(self):
        with self.assertRaises(TypeError):
            simular_fila("0,1", 5, 1)
        with self.assertRaises(TypeError):
            simular_fila([0, "1"], 5, 1)
        with self.assertRaises(TypeError):
            simular_fila([0], "5", 1)
        with self.assertRaises(TypeError):
            simular_fila([0], 5, 2.0)

    def test_bool_no_cuenta_como_numero(self):
        with self.assertRaises(TypeError):
            simular_fila([0], True, 1)
        with self.assertRaises(TypeError):
            simular_fila([0], 5, True)
        with self.assertRaises(TypeError):
            simular_fila([False], 5, 1)

    def test_parametros_invalidos_con_lista_vacia(self):
        with self.assertRaises(ValueError):
            simular_fila([], 0, 1)


class PruebasComparacionConReferencia(unittest.TestCase):

    def test_coincide_con_simulacion_segundo_a_segundo(self):
        generador = random.Random(2026)  # semilla fija: siempre los mismos casos
        for _ in range(400):
            n = generador.randint(0, 40)
            llegadas = []
            segundo = 0
            for _ in range(n):
                segundo += generador.choice([0, 0, 1, 2, 5, 13])
                llegadas.append(segundo)
            if generador.random() < 0.5:
                generador.shuffle(llegadas)  # la mitad de los casos desordenados
            frecuencia = generador.randint(1, 8)
            capacidad = generador.randint(1, 4)
            with self.subTest(llegadas=llegadas, frecuencia=frecuencia,
                              capacidad=capacidad):
                self.assertEqual(
                    simular_fila(llegadas, frecuencia, capacidad),
                    simular_segundo_a_segundo(llegadas, frecuencia, capacidad))


class PruebasVolumen(unittest.TestCase):

    def test_cientos_de_miles_todos_en_cero(self):
        n = 300000
        resultado = simular_fila([0] * n, 10, 3)
        self.assertEqual(len(resultado), n)
        self.assertEqual(resultado[:4], [10, 10, 10, 20])
        self.assertEqual(resultado[-1], ((n - 1) // 3 + 1) * 10)

    def test_cientos_de_miles_con_huecos(self):
        n = 200000
        llegadas = [i * 1000 for i in range(n)]
        resultado = simular_fila(llegadas, 7, 1)
        self.assertEqual(len(resultado), n)
        self.assertEqual(resultado[0], 7)
        for i in (1, n // 2, n - 1):
            self.assertEqual(resultado[i], ((llegadas[i] + 6) // 7) * 7)

    def test_cientos_de_miles_desordenados(self):
        generador = random.Random(7)
        n = 200000
        llegadas = [generador.randint(0, n) for _ in range(n)]
        resultado = simular_fila(llegadas, 5, 2)
        self.assertEqual(len(resultado), n)
        for i in range(n):
            self.assertGreaterEqual(resultado[i], llegadas[i])


if __name__ == "__main__":
    unittest.main()
