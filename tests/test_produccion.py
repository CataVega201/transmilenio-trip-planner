"""La entrada pública conserva la API y limita mediciones concurrentes."""
import unittest
from unittest.mock import patch
import produccion


class ProduccionTests(unittest.TestCase):
    def test_dos_mediciones_no_ocupan_memoria_a_la_vez(self):
        produccion._medicion.acquire()
        try:
            respuesta = produccion.app.test_client().post(
                "/api/rendimiento", json={"tamanos": [10], "repeticiones": 1})
            self.assertEqual(respuesta.status_code, 429)
        finally:
            produccion._medicion.release()

    def test_libera_medicion_si_el_motor_falla(self):
        with patch.object(produccion, "medir_api", side_effect=RuntimeError("fallo")):
            with self.assertRaises(RuntimeError):
                produccion.medir_publico([10], 1)
        with patch.object(produccion, "medir_api", return_value=[]) as medir:
            self.assertEqual(produccion.medir_publico([10], 1), [])
            medir.assert_called_once_with([10], 1)

    def test_salud_sin_arrancar_servidor_de_desarrollo(self):
        r = produccion.app.test_client().get("/api/estado")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json["estado"], "ok")
