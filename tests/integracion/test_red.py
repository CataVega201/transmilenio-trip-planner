"""Pruebas de integracion de Red con una red pequena hecha a mano.

Comprueban que los modulos de todos funcionan juntos detras de la fachada Red,
segun docs/CONTRATOS.md (seccion 3). Se saltan mientras `from motor import Red`
no exista. Si la fachada está integrada por bloques, se omiten únicamente
las pruebas que requieren un índice explícitamente pendiente.

Red de prueba (nombres inventados, distintos de los CSV reales):

    R1: ALFA -> BRAVO -> CHARLIE -> DELTA
    R2: CHARLIE -> ECO -> FOXTROT
    R3: GOLF -> HOTEL            (sin conexion con las demas)
    INDIA no pertenece a ninguna ruta.

Ejecutar:
    .\\.venv\\Scripts\\python.exe -m unittest discover -s tests/integracion -p "test_*.py" -v
"""

import csv
import os
import random
import tempfile
import unittest

from motor import Red

ESTACIONES = ["ALFA", "BRAVO", "CHARLIE", "DELTA", "ECO", "FOXTROT", "GOLF", "HOTEL", "INDIA"]
RUTAS = {
    "R1": ["ALFA", "BRAVO", "CHARLIE", "DELTA"],
    "R2": ["CHARLIE", "ECO", "FOXTROT"],
    "R3": ["GOLF", "HOTEL"],
}
HORARIOS = [
    ("R1", "ALFA", "05:00"), ("R1", "ALFA", "05:30"), ("R1", "ALFA", "25:10"),
    ("R1", "BRAVO", "05:05"), ("R1", "CHARLIE", "05:10"), ("R1", "DELTA", "05:15"),
    ("R2", "CHARLIE", "06:00"), ("R2", "CHARLIE", "06:30"), ("R2", "CHARLIE", "07:00"),
    ("R2", "ECO", "06:05"), ("R2", "FOXTROT", "06:10"),
    ("R3", "GOLF", "08:00"), ("R3", "HOTEL", "08:05"),
]


def escribir_red(carpeta):
    """Escribe los tres CSV con las filas mezcladas (el motor no debe suponer orden)."""
    azar = random.Random(11)
    filas_rutas = [[ruta, orden, estacion] for ruta, paradas in RUTAS.items()
                   for orden, estacion in enumerate(paradas, start=1)]
    filas_horarios = [list(fila) for fila in HORARIOS]
    nombres = [[n] for n in ESTACIONES]
    for filas in (filas_rutas, filas_horarios, nombres):
        azar.shuffle(filas)
    for archivo, encabezado, filas in [
        ("estaciones.csv", ["nombre"], nombres),
        ("rutas.csv", ["ruta", "orden", "estacion"], filas_rutas),
        ("horarios.csv", ["ruta", "estacion", "hora"], filas_horarios),
    ]:
        with open(os.path.join(carpeta, archivo), "w", encoding="utf-8", newline="") as f:
            escritor = csv.writer(f)
            escritor.writerow(encabezado)
            escritor.writerows(filas)


class PruebasRed(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        carpeta = os.path.join(self.tmp.name, "red de prueba")
        os.makedirs(carpeta)
        escribir_red(carpeta)
        self.red = Red(carpeta)

    def tearDown(self):
        self.tmp.cleanup()

    # --- Carga y consultas basicas -----------------------------------------

    def test_carga_deja_todo_abierto_y_sin_historial(self):
        for nombre in ESTACIONES:
            self.assertEqual(self.red.estado(nombre), "ABIERTA")
        self.assertEqual(self.red.estado("ZULU"), "NO EXISTE")
        self.assertFalse(self.red.deshacer())
        self.assertFalse(self.red.rehacer())

    def test_nombres_normalizados_al_consultar(self):
        self.assertEqual(self.red.estado("  alfa "), "ABIERTA")
        self.assertEqual(self.red.autocompletar("cha", 5), ["CHARLIE"])

    def test_autocompletar_y_rango(self):
        self.assertEqual(self.red.autocompletar("", 3), ["ALFA", "BRAVO", "CHARLIE"])
        self.assertEqual(self.red.autocompletar("Z", 3), [])
        self.assertEqual(self.red.autocompletar("A", 0), [])
        self.assertEqual(self.red.rango("BRAVO", "ECO"), ["BRAVO", "CHARLIE", "DELTA", "ECO"])
        self.assertEqual(self.red.rango("ECO", "BRAVO"), [])

    def test_recorridos_en_ambos_sentidos(self):
        self.assertEqual(self.red.recorrido("R1"), RUTAS["R1"])
        self.assertEqual(self.red.recorrido("R1", al_reves=True), RUTAS["R1"][::-1])
        self.assertEqual(self.red.recorrido("R9"), [])

    def test_proximo_bus(self):
        self.assertEqual(self.red.proximo_bus("ALFA", "R1", "05:10"), "05:30")
        self.assertEqual(self.red.proximo_bus("ALFA", "R1", "05:30"), "05:30")
        self.assertEqual(self.red.proximo_bus("ALFA", "R1", "06:00"), "25:10")
        self.assertIsNone(self.red.proximo_bus("ALFA", "R1", "25:11"))
        self.assertIsNone(self.red.proximo_bus("ECO", "R1", "05:00"))
        with self.assertRaises(ValueError):
            self.red.proximo_bus("ALFA", "R1", "5 y media")

    def test_ranking(self):
        ranking = self.red.ranking(3)
        self.assertEqual(ranking[0], ("CHARLIE", 4))
        self.assertEqual(ranking[1], ("ALFA", 3))
        self.assertEqual(len(ranking), 3)
        completo = self.red.ranking(20)
        self.assertIn(("INDIA", 0), completo)
        cuentas = [c for _, c in completo]
        self.assertEqual(cuentas, sorted(cuentas, reverse=True))

    def test_viajes(self):
        self.assertEqual(self.red.viaje("ALFA", "DELTA"), [("R1", "ALFA", "DELTA")])
        self.assertEqual(self.red.viaje("ALFA", "FOXTROT"),
                         [("R1", "ALFA", "CHARLIE"), ("R2", "CHARLIE", "FOXTROT")])
        self.assertIsNone(self.red.viaje("ALFA", "GOLF"))
        self.assertIsNone(self.red.viaje("DELTA", "ALFA"))  # se sigue el sentido de la ruta
        self.assertEqual(self.red.viaje("ALFA", "ALFA"), [])
        self.assertIsNone(self.red.viaje("ZULU", "ALFA"))

    # --- Cierres (R8) y su efecto en las demas consultas -------------------

    def test_cerrar_afecta_todas_las_consultas(self):
        self.assertTrue(self.red.cerrar("BRAVO"))
        self.assertFalse(self.red.cerrar("BRAVO"))
        self.assertFalse(self.red.cerrar("ZULU"))
        self.assertEqual(self.red.estado("BRAVO"), "CERRADA")
        self.assertNotIn("BRAVO", self.red.autocompletar("", 10))
        self.assertNotIn("BRAVO", self.red.rango("ALFA", "DELTA"))
        self.assertNotIn("BRAVO", [n for n, _ in self.red.ranking(20)])
        self.assertIsNone(self.red.proximo_bus("BRAVO", "R1", "05:00"))
        self.assertIn("BRAVO", self.red.recorrido("R1"))  # el operador la sigue viendo
        # Se puede atravesar a bordo, pero no subir ni bajar alli.
        self.assertEqual(self.red.viaje("ALFA", "DELTA"), [("R1", "ALFA", "DELTA")])
        self.assertIsNone(self.red.viaje("ALFA", "BRAVO"))
        self.assertIsNone(self.red.viaje("BRAVO", "BRAVO"))

    def test_cerrar_estacion_de_transbordo_impide_el_viaje(self):
        self.assertTrue(self.red.cerrar("CHARLIE"))
        self.assertIsNone(self.red.viaje("ALFA", "FOXTROT"))
        self.assertTrue(self.red.reabrir("CHARLIE"))
        self.assertIsNotNone(self.red.viaje("ALFA", "FOXTROT"))

    def test_reabrir(self):
        self.assertFalse(self.red.reabrir("ALFA"))
        self.red.cerrar("ALFA")
        self.assertTrue(self.red.reabrir("ALFA"))
        self.assertEqual(self.red.estado("ALFA"), "ABIERTA")
        self.assertIn("ALFA", self.red.autocompletar("A", 5))

    # --- Edicion de rutas (R7) ---------------------------------------------

    def test_agregar_y_quitar_paradas(self):
        self.assertTrue(self.red.agregar_parada("R2", "INDIA", "ECO"))
        self.assertEqual(self.red.recorrido("R2"), ["CHARLIE", "ECO", "INDIA", "FOXTROT"])
        self.assertFalse(self.red.agregar_parada("R2", "INDIA", "CHARLIE"))  # ya esta
        self.assertFalse(self.red.agregar_parada("R2", "ZULU", "ECO"))       # no existe
        self.assertFalse(self.red.agregar_parada("R9", "INDIA", "ECO"))      # ruta ausente
        self.assertFalse(self.red.agregar_parada("R2", "GOLF", "DELTA"))     # despues_de ausente
        self.assertTrue(self.red.agregar_parada("R3", "INDIA", "HOTEL"))     # despues de la ultima
        self.assertEqual(self.red.recorrido("R3"), ["GOLF", "HOTEL", "INDIA"])
        self.assertTrue(self.red.quitar_parada("R1", "BRAVO"))
        self.assertFalse(self.red.quitar_parada("R1", "BRAVO"))
        self.assertEqual(self.red.recorrido("R1"), ["ALFA", "CHARLIE", "DELTA"])

    def test_quitar_parada_desactiva_sus_horarios_y_su_ranking(self):
        self.assertTrue(self.red.quitar_parada("R2", "CHARLIE"))
        self.assertIsNone(self.red.proximo_bus("CHARLIE", "R2", "05:00"))
        self.assertIn(("CHARLIE", 1), self.red.ranking(20))
        self.assertIsNone(self.red.viaje("ALFA", "FOXTROT"))
        self.assertTrue(self.red.deshacer())
        self.assertEqual(self.red.proximo_bus("CHARLIE", "R2", "05:00"), "06:00")
        self.assertEqual(self.red.ranking(1), [("CHARLIE", 4)])

    def test_nueva_parada_no_inventa_horarios(self):
        self.red.agregar_parada("R2", "INDIA", "ECO")
        self.assertIsNone(self.red.proximo_bus("INDIA", "R2", "05:00"))
        self.assertIn(("INDIA", 0), self.red.ranking(20))

    # --- Historial (R9) ------------------------------------------------------

    def test_deshacer_y_rehacer_mezclando_acciones(self):
        self.red.cerrar("ECO")
        self.red.agregar_parada("R1", "INDIA", "DELTA")
        self.assertTrue(self.red.deshacer())
        self.assertEqual(self.red.recorrido("R1"), RUTAS["R1"])
        self.assertTrue(self.red.deshacer())
        self.assertEqual(self.red.estado("ECO"), "ABIERTA")
        self.assertFalse(self.red.deshacer())
        self.assertTrue(self.red.rehacer())
        self.assertEqual(self.red.estado("ECO"), "CERRADA")
        self.assertTrue(self.red.rehacer())
        self.assertEqual(self.red.recorrido("R1")[-1], "INDIA")
        self.assertFalse(self.red.rehacer())

    def test_operaciones_sin_efecto_no_entran_al_historial(self):
        self.red.cerrar("ECO")
        self.red.deshacer()
        self.assertFalse(self.red.cerrar("ZULU"))
        self.assertFalse(self.red.quitar_parada("R1", "ECO"))
        self.red.estado("ALFA")
        self.assertTrue(self.red.rehacer())  # rehacer sigue disponible

    def test_cambio_nuevo_vacia_rehacer(self):
        self.red.cerrar("ECO")
        self.red.deshacer()
        self.assertTrue(self.red.cerrar("DELTA"))
        self.assertFalse(self.red.rehacer())
        self.assertEqual(self.red.estado("ECO"), "ABIERTA")

    def test_respuestas_son_datos_simples(self):
        """El motor no devuelve diccionarios ni conjuntos (contrato del profesor)."""
        respuestas = [
            self.red.autocompletar("", 3), self.red.rango("ALFA", "ECO"),
            self.red.ranking(3), self.red.recorrido("R1"), self.red.viaje("ALFA", "FOXTROT"),
        ]
        for respuesta in respuestas:
            self.assertIsInstance(respuesta, list)
            for elemento in respuesta:
                self.assertNotIsInstance(elemento, (dict, set))


if __name__ == "__main__":
    unittest.main()
