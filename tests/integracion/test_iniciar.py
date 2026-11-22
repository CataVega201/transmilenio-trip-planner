"""Pruebas del arranque unico (iniciar.py), sin abrir navegador ni servidor."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import iniciar


class PruebasDatos(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.carpeta = Path(self.tmp.name) / "datos con espacios"
        self.carpeta.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def crear_csv(self, nombres=iniciar.CSV_REQUERIDOS):
        for nombre in nombres:
            (self.carpeta / nombre).write_text("x\n", encoding="utf-8")

    def test_acepta_carpeta_completa_con_espacios(self):
        self.crear_csv()
        self.assertEqual(iniciar.carpeta_de_datos(str(self.carpeta)), self.carpeta.resolve())

    def test_avisa_los_csv_que_faltan(self):
        self.crear_csv(["estaciones.csv"])
        with self.assertRaises(iniciar.ErrorArranque) as error:
            iniciar.carpeta_de_datos(str(self.carpeta))
        self.assertIn("rutas.csv", str(error.exception))
        self.assertIn("horarios.csv", str(error.exception))

    def test_avisa_si_la_carpeta_no_existe(self):
        with self.assertRaises(iniciar.ErrorArranque):
            iniciar.carpeta_de_datos(str(self.carpeta / "no_esta"))

    def test_carpeta_relativa_al_proyecto(self):
        actual = os.getcwd()
        os.chdir(self.tmp.name)
        try:
            ruta = iniciar.carpeta_de_datos("datos")
        finally:
            os.chdir(actual)
        self.assertEqual(ruta, (iniciar.RAIZ / "datos").resolve())


class PruebasCompilacion(unittest.TestCase):

    def test_sin_npm_y_sin_dist_explica_que_instalar(self):
        with mock.patch.object(iniciar.shutil, "which", return_value=None), \
                mock.patch.object(iniciar, "DIST", Path(tempfile.gettempdir()) / "no_existe_dist"):
            with self.assertRaises(iniciar.ErrorArranque) as error:
                iniciar.compilar_pagina(False)
        self.assertIn("Node.js", str(error.exception))

    def test_sin_npm_usa_dist_existente(self):
        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp)
            (dist / "index.html").write_text("<html></html>", encoding="utf-8")
            with mock.patch.object(iniciar.shutil, "which", return_value=None), \
                    mock.patch.object(iniciar, "DIST", dist):
                self.assertEqual(iniciar.compilar_pagina(False), dist)

    def test_sin_compilar_exige_dist(self):
        with mock.patch.object(iniciar, "DIST", Path(tempfile.gettempdir()) / "no_existe_dist"):
            with self.assertRaises(iniciar.ErrorArranque):
                iniciar.compilar_pagina(True)

    def test_no_instala_nada_si_faltan_dependencias(self):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(iniciar.shutil, "which", return_value="npm"), \
                mock.patch.object(iniciar, "FRONTEND", Path(tmp)), \
                mock.patch.object(iniciar.subprocess, "run") as correr:
            with self.assertRaises(iniciar.ErrorArranque) as error:
                iniciar.compilar_pagina(False)
        correr.assert_not_called()
        self.assertIn("npm --prefix frontend install", str(error.exception))


class PruebasServidor(unittest.TestCase):

    def test_sirve_pagina_y_api_en_un_solo_servidor(self):
        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp) / "dist con espacios"
            (dist / "assets").mkdir(parents=True)
            (dist / "index.html").write_text("<h1>planeador</h1>", encoding="utf-8")
            (dist / "assets" / "app.js").write_text("console.log(1)", encoding="utf-8")
            cliente = iniciar.crear_aplicacion(iniciar.RAIZ / "datos", dist).test_client()
            with cliente.get("/") as respuesta:
                self.assertIn(b"planeador", respuesta.data)
            with cliente.get("/assets/app.js") as respuesta:
                self.assertEqual(respuesta.status_code, 200)
            self.assertEqual(cliente.get("/api/estado").json["estado"], "ok")

    def test_main_devuelve_1_con_error_claro(self):
        with mock.patch("sys.stderr") as salida:
            codigo = iniciar.main(["--datos", "carpeta_que_no_existe", "--no-abrir"])
        self.assertEqual(codigo, 1)
        self.assertTrue(salida.write.called)


if __name__ == "__main__":
    unittest.main()
