"""Pruebas de R4. Se completaran al implementar el indice de horarios."""

import unittest

from motor.horarios import _buscar_siguiente, _ordenar_horarios, hora_a_minutos


class ConversionDeHorasTests(unittest.TestCase):
    def test_limites_del_dia(self):
        self.assertEqual(hora_a_minutos("00:00"), 0)
        self.assertEqual(hora_a_minutos("23:59"), 1439)

    def test_horas_del_dia_de_servicio_no_se_reinician(self):
        self.assertEqual(hora_a_minutos("24:00"), 1440)
        self.assertEqual(hora_a_minutos("25:10"), 1510)
        self.assertEqual(hora_a_minutos("100:05"), 6005)

    def test_horas_con_ceros_iniciales(self):
        self.assertEqual(hora_a_minutos("08:05"), 485)

    def test_rechaza_minutos_fuera_de_rango(self):
        for hora in ["00:60", "25:99"]:
            with self.subTest(hora=hora):
                with self.assertRaises(ValueError):
                    hora_a_minutos(hora)

    def test_rechaza_formatos_invalidos(self):
        for hora in ["", "8:05", "08:5", "08:05:00", "-1:00", "AA:10",
                     "08-05", " 08:05", "08:05 ", "0:0:00", "08:0A"]:
            with self.subTest(hora=hora):
                with self.assertRaises(ValueError):
                    hora_a_minutos(hora)

    def test_rechaza_entradas_que_no_son_texto(self):
        for hora in [None, 810, True, ["08:10"]]:
            with self.subTest(hora=hora):
                with self.assertRaises(TypeError):
                    hora_a_minutos(hora)


class BusquedaDelSiguienteTests(unittest.TestCase):
    def test_sin_buses(self):
        self.assertIsNone(_buscar_siguiente([], 480))

    def test_antes_del_primer_bus(self):
        self.assertEqual(_buscar_siguiente([480, 490, 500], 470), 480)

    def test_hora_exacta_y_ultimo_bus(self):
        self.assertEqual(_buscar_siguiente([480, 490, 500], 490), 490)
        self.assertEqual(_buscar_siguiente([480, 490, 500], 500), 500)

    def test_entre_dos_buses(self):
        self.assertEqual(_buscar_siguiente([480, 490, 500], 491), 500)

    def test_despues_del_ultimo_bus(self):
        self.assertIsNone(_buscar_siguiente([480, 490, 500], 501))

    def test_un_solo_bus(self):
        self.assertEqual(_buscar_siguiente([480], 479), 480)
        self.assertEqual(_buscar_siguiente([480], 480), 480)
        self.assertIsNone(_buscar_siguiente([480], 481))

    def test_horarios_repetidos(self):
        self.assertEqual(_buscar_siguiente([480, 480, 480, 490], 480), 480)
        self.assertEqual(_buscar_siguiente([480, 480, 480, 490], 481), 490)

    def test_continua_despues_de_medianoche(self):
        self.assertEqual(_buscar_siguiente([1430, 1445, 1510], 1440), 1445)
        self.assertEqual(_buscar_siguiente([1430, 1445, 1510], 1500), 1510)

    def test_no_modifica_los_horarios(self):
        horarios = [480, 490, 500]
        _buscar_siguiente(horarios, 485)
        self.assertEqual(horarios, [480, 490, 500])

    def test_coincide_con_oraculo_lineal_en_casos_aleatorios(self):
        # Las restricciones del motor no aplican al oraculo independiente.
        import random

        generador = random.Random(42)
        for _ in range(100):
            horarios = sorted(generador.randrange(1800)
                              for _ in range(generador.randrange(80)))
            minuto = generador.randrange(2000)
            esperado = next((hora for hora in horarios if hora >= minuto), None)
            with self.subTest(horarios=horarios, minuto=minuto):
                self.assertEqual(_buscar_siguiente(horarios, minuto), esperado)


class OrdenacionDeHorariosTests(unittest.TestCase):
    def test_limites_duplicados_y_orden_inverso(self):
        for entrada in [[], [480], [500, 490, 480], [480, 480, 490],
                        [1510, 0, 1440, 480, 1510], [0, 1, 2, 3, 4]]:
            with self.subTest(entrada=entrada):
                esperado = sorted(entrada)
                horarios = entrada.copy()
                _ordenar_horarios(horarios)
                self.assertEqual(horarios, esperado)

    def test_tamanos_variados_con_oraculo_independiente(self):
        import random

        generador = random.Random(84)
        for cantidad in range(130):
            horarios = [generador.randrange(2000) for _ in range(cantidad)]
            esperado = sorted(horarios)
            with self.subTest(cantidad=cantidad):
                _ordenar_horarios(horarios)
                self.assertEqual(horarios, esperado)

    def test_conversion_ordenacion_y_consulta_juntas(self):
        horarios = [hora_a_minutos(hora)
                    for hora in ["25:10", "08:00", "24:05", "08:00"]]
        _ordenar_horarios(horarios)
        self.assertEqual(horarios, [480, 480, 1445, 1510])
        self.assertEqual(_buscar_siguiente(horarios, hora_a_minutos("23:59")), 1445)


if __name__ == "__main__":
    unittest.main()
