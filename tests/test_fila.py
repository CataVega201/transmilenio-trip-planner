"""Pruebas de R10 - simular_fila.

Ejecutar desde la carpeta del proyecto:
    .\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_fila.py" -v
"""

import random
import time
import unittest

from motor.fila import ColaFIFO, simular_fila


def simular_minuto_a_minuto(llegadas, frecuencia, capacidad):
    """Version ingenua de referencia (solo para pruebas, fuera de motor/).

    Recorre cada minuto desde 0 y usa una lista normal. Es lenta, pero
    facil de comprobar a mano; sirve para comparar con la version real.
    """
    resultado = []
    fila = []
    i = 0
    minuto = 0
    n = len(llegadas)
    while i < n or fila:
        while i < n and llegadas[i] == minuto:
            fila.append(llegadas[i])
            i += 1
        if minuto % frecuencia == 0:
            suben = fila[:capacidad]
            fila = fila[capacidad:]
            for llegada in suben:
                resultado.append([llegada, minuto, minuto - llegada])
        minuto += 1
    return resultado


class PruebasCola(unittest.TestCase):

    def test_fifo_con_crecimiento_y_vuelta(self):
        cola = ColaFIFO(2)
        cola.encolar(1)
        cola.encolar(2)
        self.assertEqual(cola.desencolar(), 1)
        # Fuerza la vuelta circular y luego el crecimiento.
        for valor in range(3, 10):
            cola.encolar(valor)
        salida = []
        while not cola.vacia():
            salida.append(cola.desencolar())
        self.assertEqual(salida, [2, 3, 4, 5, 6, 7, 8, 9])

    def test_desencolar_vacia(self):
        with self.assertRaises(IndexError):
            ColaFIFO().desencolar()


class PruebasEjemplosContrato(unittest.TestCase):

    def test_ejemplo_1(self):
        self.assertEqual(
            simular_fila([0, 0, 1, 10], 10, 2),
            [[0, 0, 0], [0, 0, 0], [1, 10, 9], [10, 10, 0]])

    def test_ejemplo_2(self):
        self.assertEqual(
            simular_fila([0, 0, 0], 10, 2),
            [[0, 0, 0], [0, 0, 0], [0, 10, 10]])


class PruebasCasosNormales(unittest.TestCase):

    def test_lista_vacia(self):
        self.assertEqual(simular_fila([], 5, 3), [])

    def test_una_llegada_en_cero(self):
        self.assertEqual(simular_fila([0], 7, 1), [[0, 0, 0]])

    def test_llegada_entre_buses(self):
        # Bus en 0, 5, 10: quien llega en 3 sube en 5.
        self.assertEqual(simular_fila([3], 5, 1), [[3, 5, 2]])

    def test_llegada_justo_con_el_bus(self):
        self.assertEqual(simular_fila([5], 5, 1), [[5, 5, 0]])

    def test_personas_simultaneas(self):
        self.assertEqual(
            simular_fila([4, 4, 4], 5, 3),
            [[4, 5, 1], [4, 5, 1], [4, 5, 1]])

    def test_cupo_exacto(self):
        self.assertEqual(
            simular_fila([0, 0, 0], 10, 3),
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]])

    def test_una_mas_que_el_cupo(self):
        self.assertEqual(
            simular_fila([0, 0, 0, 0], 10, 3),
            [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 10, 10]])

    def test_varias_salidas_seguidas(self):
        # 5 personas, cupo 2, bus cada 3: salen en 0, 3 y 6.
        self.assertEqual(
            simular_fila([0, 0, 0, 0, 0], 3, 2),
            [[0, 0, 0], [0, 0, 0], [0, 3, 3], [0, 3, 3], [0, 6, 6]])

    def test_fifo_quien_espera_sube_antes(self):
        # Llegan 2 en 0 (cupo 1) y 1 en 10. En 10 sube primero quien
        # esperaba desde 0, no el recien llegado.
        self.assertEqual(
            simular_fila([0, 0, 10], 10, 1),
            [[0, 0, 0], [0, 10, 10], [10, 20, 10]])

    def test_gran_salto_de_tiempo(self):
        inicio = time.perf_counter()
        resultado = simular_fila([0, 1000000, 1000000000], 7, 1)
        duracion = time.perf_counter() - inicio
        self.assertEqual(resultado, [
            [0, 0, 0],
            [1000000, 1000006, 6],
            # 1000000000 = 7 * 142857142 + 6, el bus siguiente es 1000000001.
            [1000000000, 1000000001, 1],
        ])
        # Sin recorrer minutos vacios debe ser practicamente instantaneo.
        self.assertLess(duracion, 0.1)

    def test_no_modifica_la_entrada(self):
        llegadas = [0, 0, 1]
        simular_fila(llegadas, 2, 1)
        self.assertEqual(llegadas, [0, 0, 1])

    def test_acepta_tupla(self):
        self.assertEqual(simular_fila((0, 1), 1, 1), [[0, 0, 0], [1, 1, 0]])


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

    def test_llegadas_desordenadas(self):
        with self.assertRaises(ValueError):
            simular_fila([0, 5, 3], 5, 1)

    def test_llegada_negativa(self):
        with self.assertRaises(ValueError):
            simular_fila([-1, 0], 5, 1)

    def test_tipos_incompatibles(self):
        with self.assertRaises(TypeError):
            simular_fila("0,1", 5, 1)
        with self.assertRaises(TypeError):
            simular_fila([0, 1.5], 5, 1)
        with self.assertRaises(TypeError):
            simular_fila([0], 5.0, 1)
        with self.assertRaises(TypeError):
            simular_fila([0], 5, "2")

    def test_bool_no_cuenta_como_entero(self):
        with self.assertRaises(TypeError):
            simular_fila([0], True, 1)
        with self.assertRaises(TypeError):
            simular_fila([0], 5, True)
        with self.assertRaises(TypeError):
            simular_fila([False], 5, 1)

    def test_parametros_invalidos_con_lista_vacia(self):
        # Se valida aunque no haya pasajeros.
        with self.assertRaises(ValueError):
            simular_fila([], 0, 1)


class PruebasComparacionConReferencia(unittest.TestCase):

    def test_coincide_con_simulacion_minuto_a_minuto(self):
        generador = random.Random(2026)  # semilla fija: siempre los mismos casos
        for _ in range(300):
            n = generador.randint(0, 40)
            llegadas = []
            minuto = 0
            for _ in range(n):
                minuto += generador.choice([0, 0, 1, 2, 5, 13])
                llegadas.append(minuto)
            frecuencia = generador.randint(1, 8)
            capacidad = generador.randint(1, 4)
            with self.subTest(llegadas=llegadas, frecuencia=frecuencia,
                              capacidad=capacidad):
                self.assertEqual(
                    simular_fila(llegadas, frecuencia, capacidad),
                    simular_minuto_a_minuto(llegadas, frecuencia, capacidad))


class PruebasVolumen(unittest.TestCase):

    def test_cientos_de_miles_todos_en_cero(self):
        # Peor caso de espacio de la cola: todos esperan a la vez.
        n = 300000
        resultado = simular_fila([0] * n, 10, 3)
        self.assertEqual(len(resultado), n)
        self.assertEqual(resultado[0], [0, 0, 0])
        self.assertEqual(resultado[2], [0, 0, 0])
        self.assertEqual(resultado[3], [0, 10, 10])
        ultimo_bus = ((n - 1) // 3) * 10
        self.assertEqual(resultado[-1], [0, ultimo_bus, ultimo_bus])

    def test_cientos_de_miles_con_huecos(self):
        n = 200000
        llegadas = [i * 1000 for i in range(n)]
        resultado = simular_fila(llegadas, 7, 1)
        self.assertEqual(len(resultado), n)
        for i in (0, 1, n // 2, n - 1):
            llegada = llegadas[i]
            bus = ((llegada + 6) // 7) * 7
            self.assertEqual(resultado[i], [llegada, bus, bus - llegada])


if __name__ == "__main__":
    unittest.main()
