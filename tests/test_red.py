"""Pruebas de la carga y las operaciones integradas de Red."""
import csv
import random
import tempfile
import unittest
from pathlib import Path

from motor import Red
from motor.red import ModuloPendiente
from servidor import crear_app


class RedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.carpeta = Path(self.tmp.name) / "red con espacios"
        self.carpeta.mkdir()
        self.nombres = ["Álfa", "Bravo", "Cambio", "Destino", "Isla", "Ñandú"]
        self.rutas = {"Línea A": ["Álfa", "Bravo", "Cambio"],
                      "Línea B": ["Cambio", "Destino"], "Otra": ["Isla"]}
        self.horas = [("Línea A", "Álfa", "25:10"), ("Línea A", "Álfa", "05:30"),
                      ("Línea A", "Álfa", "05:30"), ("Línea B", "Cambio", "06:00")]
        self.escribir()

    def escribir(self):
        filas = [(ruta, i + 1, nombre) for ruta, paradas in self.rutas.items()
                 for i, nombre in enumerate(paradas)]
        for archivo, cabecera, datos in [
            ("estaciones.csv", ["nombre"], [(n,) for n in self.nombres]),
            ("rutas.csv", ["ruta", "orden", "estacion"], filas),
            ("horarios.csv", ["ruta", "estacion", "hora"], self.horas),
        ]:
            datos = list(datos)
            random.Random(2026).shuffle(datos)
            with (self.carpeta / archivo).open("w", encoding="utf-8-sig", newline="") as f:
                w = csv.writer(f)
                w.writerow(cabecera)
                w.writerows(datos)

    def red(self):
        return Red(str(self.carpeta))

    def test_carga_preserva_nombres_y_consulta_normalizada(self):
        r = self.red()
        self.assertEqual(r.recorrido(" linea a "), self.rutas["Línea A"])
        self.assertEqual(r.estado(" alfa "), "ABIERTA")
        self.assertEqual(r.estado("nandu"), "NO EXISTE")
        self.assertEqual(r.estado("ñandu"), "ABIERTA")
        self.assertEqual(r.recorrido("LÍNEA A", True), self.rutas["Línea A"][::-1])
        self.assertFalse(r.deshacer())

    def test_horarios_duplicados_extendidos_y_limites(self):
        r = self.red()
        self.assertEqual(r.proximo_bus("alfa", "linea a", "05:30"), "05:30")
        self.assertEqual(r.proximo_bus("alfa", "linea a", "05:31"), "25:10")
        self.assertIsNone(r.proximo_bus("alfa", "linea a", "25:11"))
        self.assertIsNone(r.proximo_bus("Isla", "linea a", "05:00"))
        self.assertEqual(dict(r.conteos_vigentes())["Álfa"], 3)
        with self.assertRaises(ValueError):
            r.proximo_bus("ausente", "ausente", "mal")

    def test_viajes_y_estaciones_cerradas(self):
        r = self.red()
        esperado = [("Línea A", "Álfa", "Cambio"), ("Línea B", "Cambio", "Destino")]
        self.assertEqual(r.viaje("alfa", "destino"), esperado)
        self.assertIsNone(r.viaje("Destino", "Álfa"))
        self.assertEqual(r.viaje("Álfa", "Álfa"), [])
        self.assertIsNone(r.viaje("Álfa", "Isla"))
        r.cerrar("Bravo")
        self.assertEqual(r.viaje("Álfa", "Destino"), esperado)
        r.cerrar("Cambio")
        self.assertIsNone(r.viaje("Álfa", "Destino"))
        r.reabrir("Cambio")
        self.assertEqual(r.viaje("Álfa", "Destino"), esperado)
        r.cerrar("Álfa")
        self.assertIsNone(r.viaje("Álfa", "Álfa"))
        self.assertIsNone(r.proximo_bus("Álfa", "Línea A", "05:00"))

    def test_edicion_restaura_primera_ultima_y_unica(self):
        for ruta, nombre in [("Línea A", "Álfa"), ("Línea A", "Cambio"), ("Otra", "Isla")]:
            with self.subTest(ruta=ruta, nombre=nombre):
                r = self.red()
                original = r.recorrido(ruta)
                cuentas = dict(r.conteos_vigentes())
                self.assertTrue(r.quitar_parada(ruta, nombre))
                self.assertTrue(r.deshacer())
                self.assertEqual(r.recorrido(ruta), original)
                self.assertEqual(dict(r.conteos_vigentes()), cuentas)
                self.assertTrue(r.rehacer())
                self.assertNotIn(nombre, r.recorrido(ruta))

    def test_historial_mixto_y_conteos(self):
        r = self.red()
        self.assertFalse(r.rehacer())
        self.assertTrue(r.quitar_parada("Línea A", "Álfa"))
        self.assertEqual(dict(r.conteos_vigentes())["Álfa"], 0)
        self.assertIsNone(r.proximo_bus("Álfa", "Línea A", "05:00"))
        self.assertTrue(r.agregar_parada("Línea A", "Álfa", "Bravo"))
        self.assertEqual(dict(r.conteos_vigentes())["Álfa"], 3)
        r.cerrar("Álfa")
        self.assertNotIn("Álfa", dict(r.conteos_vigentes()))
        self.assertTrue(r.deshacer())
        self.assertTrue(r.deshacer())
        self.assertTrue(r.deshacer())
        self.assertEqual(r.recorrido("Línea A"), self.rutas["Línea A"])
        self.assertEqual(dict(r.conteos_vigentes())["Álfa"], 3)
        self.assertFalse(r.cerrar("ausente"))
        self.assertFalse(r.quitar_parada("Línea A", "Isla"))
        self.assertTrue(r.rehacer())
        self.assertTrue(r.cerrar("Destino"))
        self.assertFalse(r.rehacer())

    def test_agregar_no_crea_estacion_ruta_ni_horario(self):
        r = self.red()
        self.assertFalse(r.agregar_parada("inexistente", "Isla", "Bravo"))
        self.assertFalse(r.agregar_parada("Línea A", "nueva", "Bravo"))
        self.assertFalse(r.agregar_parada("Línea A", "Álfa", "Bravo"))
        self.assertFalse(r.agregar_parada("Línea A", "Isla", "Destino"))
        self.assertTrue(r.agregar_parada("Línea A", "Isla", "Cambio"))
        self.assertIsNone(r.proximo_bus("Isla", "Línea A", "05:00"))
        self.assertEqual(r.viaje("Álfa", "Isla"), [("Línea A", "Álfa", "Isla")])

    def test_carga_rechaza_errores_de_datos(self):
        cambios = [
            ("estaciones.csv", ["nombre"], [("A",), ("á",)]),
            ("rutas.csv", ["ruta", "orden", "estacion"], [("R", 1, "ausente")]),
            ("rutas.csv", ["ruta", "orden", "estacion"], [("R", 0, "Álfa")]),
            ("rutas.csv", ["ruta", "orden", "estacion"], [("R", 1, "Álfa"), ("R", 1, "Bravo")]),
            ("rutas.csv", ["ruta", "orden", "estacion"], [("R", 1, "Álfa"), ("R", 2, "Álfa")]),
            ("rutas.csv", ["ruta", "orden", "estacion"], [("R", 1, "Álfa"), ("r", 2, "Bravo")]),
            ("horarios.csv", ["ruta", "estacion", "hora"], [("Línea A", "Isla", "05:00")]),
            ("horarios.csv", ["ruta", "estacion", "hora"], [("Línea A", "Álfa", "25:60")]),
            ("estaciones.csv", ["otro"], []),
            ("estaciones.csv", ["nombre"], [("A", "columna extra")]),
        ]
        for archivo, cabecera, datos in cambios:
            with self.subTest(archivo=archivo, datos=datos):
                self.escribir()
                with (self.carpeta / archivo).open("w", encoding="utf-8", newline="") as f:
                    w = csv.writer(f)
                    w.writerow(cabecera)
                    w.writerows(datos)
                with self.assertRaises(ValueError):
                    self.red()

    def test_red_vacia_y_archivo_ausente(self):
        self.nombres, self.rutas, self.horas = [], {}, []
        self.escribir()
        r = self.red()
        self.assertEqual(r.estado("A"), "NO EXISTE")
        self.assertEqual(r.recorrido("A"), [])
        self.assertIsNone(r.viaje("A", "B"))
        self.assertEqual(r.conteos_vigentes(), [])
        (self.carpeta / "rutas.csv").unlink()
        with self.assertRaises(FileNotFoundError):
            self.red()

    def test_api_real_y_consultas_pendientes(self):
        c = crear_app(carpeta_datos=str(self.carpeta)).test_client()
        self.assertEqual(c.get("/api/estaciones/estado?nombre=alfa").json["datos"], "ABIERTA")
        self.assertEqual(c.get("/api/viajes?origen=alfa&destino=destino").json["datos"],
                         [["Línea A", "Álfa", "Cambio"], ["Línea B", "Cambio", "Destino"]])
        self.assertTrue(c.post("/api/estaciones/cerrar", json={"nombre": "Cambio"}).json["datos"])
        self.assertIsNone(c.get("/api/viajes?origen=alfa&destino=destino").json["datos"])
        self.assertTrue(c.post("/api/historial/deshacer", json={}).json["datos"])
        for url in ["/api/estaciones/autocompletar?prefijo=A&k=5",
                    "/api/estaciones/rango?desde=A&hasta=Z", "/api/ranking?k=5"]:
            respuesta = c.get(url)
            self.assertEqual(respuesta.status_code, 503)
            self.assertEqual(respuesta.json["error"]["codigo"], "MODULO_PENDIENTE")

    def test_viajes_aleatorios_con_referencia_exhaustiva(self):
        azar = random.Random(194)
        self.nombres = ["A", "B", "C", "D", "E", "F"]
        self.horas = []
        for caso in range(20):
            self.rutas = {f"R{i}": azar.sample(self.nombres, azar.randint(1, 6)) for i in range(5)}
            self.escribir()
            r = self.red()
            cerradas = set(azar.sample(self.nombres, 2))
            for n in cerradas:
                r.cerrar(n)
            for origen in self.nombres:
                for destino in self.nombres:
                    candidatos = []
                    if origen not in cerradas and destino not in cerradas:
                        for ruta, paradas in self.rutas.items():
                            if origen not in paradas:
                                continue
                            a = paradas.index(origen)
                            if destino in paradas and paradas.index(destino) > a:
                                candidatos.append(((paradas.index(destino) - a, 0, ruta, "", ""),
                                                   [(ruta, origen, destino)]))
                            for cambio in paradas[a + 1:]:
                                if cambio in cerradas:
                                    continue
                                for otra, siguientes in self.rutas.items():
                                    if cambio in siguientes and destino in siguientes:
                                        b, c = siguientes.index(cambio), siguientes.index(destino)
                                        if c > b:
                                            costo = paradas.index(cambio) - a + c - b
                                            candidatos.append(((costo, 1, ruta, otra, cambio),
                                                               [(ruta, origen, cambio), (otra, cambio, destino)]))
                    esperado = min(candidatos, default=(None, None), key=lambda x: x[0])[1]
                    if origen == destino and origen not in cerradas:
                        esperado = []
                    with self.subTest(caso=caso, origen=origen, destino=destino):
                        self.assertEqual(r.viaje(origen, destino), esperado)
