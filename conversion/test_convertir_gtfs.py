import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile


class ConversionGTFS(unittest.TestCase):
    def test_conversion_por_fecha_y_sentido(self):
        with TemporaryDirectory() as carpeta:
            base = Path(carpeta)
            zip_path = base / "ejemplo.zip"
            tablas = {
                "stops": "stop_id,stop_name,parent_station\ns,Estación Ñ,\na,Plataforma,s\nb,Portal,\n",
                "routes": "route_id\nR\n",
                "trips": "route_id,service_id,trip_id,direction_id\nR,S,t,0\nR,S,u,1\nR,OFF,x,0\n",
                "calendar_dates": "service_id,date,exception_type\nS,20210701,1\nOFF,20210701,2\n",
                "calendar": "service_id,start_date,end_date,thursday\nOFF,20210701,20210731,1\n",
                "stop_times": ("trip_id,stop_id,stop_sequence,arrival_time,departure_time\n"
                               "t,b,20,25:10:59,25:10:59\nt,a,10,24:00:00,24:00:00\n"
                               "u,b,1,10:00:00,10:00:00\nu,a,2,10:10:00,10:10:00\n"
                               "x,b,1,12:00:00,12:00:00\n"),
            }
            with ZipFile(zip_path, "w") as z:
                for nombre, filas in tablas.items():
                    z.writestr("red/" + nombre + ".txt", filas.encode("utf-8"))
            destino = base / "salida"
            comando = [sys.executable, str(Path(__file__).with_name("convertir_gtfs.py")),
                       str(zip_path), str(destino), "--fecha", "2021-07-01"]
            subprocess.run(comando, check=True, capture_output=True)
            self.assertEqual((destino/"estaciones.csv").read_text("utf-8").splitlines(),
                             ["nombre", "ESTACION Ñ", "PORTAL"])
            self.assertEqual((destino/"rutas.csv").read_text("utf-8").splitlines(),
                             ["ruta,orden,estacion", "R-0-1,1,ESTACION Ñ", "R-0-1,2,PORTAL",
                              "R-1-1,1,PORTAL", "R-1-1,2,ESTACION Ñ"])
            horarios = (destino/"horarios.csv").read_text("utf-8").splitlines()
            self.assertEqual(horarios, ["ruta,estacion,hora", "R-0-1,ESTACION Ñ,24:00",
                                        "R-0-1,PORTAL,25:10", "R-1-1,PORTAL,10:00",
                                        "R-1-1,ESTACION Ñ,10:10"])
            self.assertNotEqual(subprocess.run(comando, capture_output=True).returncode, 0)

    def test_troncal_agrupa_plataformas_y_excluye_rutas_urbanas(self):
        from datetime import date
        from conversion.convertir_gtfs import convertir
        with TemporaryDirectory() as carpeta:
            base = Path(carpeta)
            tablas = {
                "calendar_dates": "service_id,date,exception_type\nS,20210714,1\n",
                "routes": "route_id,route_desc\nR,TRONCAL\nU,URBANO\n",
                "trips": "route_id,service_id,trip_id\nR,S,t\nU,S,u\n",
                "stops": "stop_id,stop_name\na,San Mateo C - 2 ó 5\nb,San Mateo C - 4 ó 6\nc,Portal Sur T9\n",
                "stop_times": ("trip_id,stop_id,stop_sequence,arrival_time,departure_time\n"
                               "t,a,0,04:00:00,04:00:00\nt,b,1,04:03:20,04:03:20\n"
                               "t,c,2,04:10:00,04:10:00\nu,a,0,23:00:00,23:00:00\n"),
            }
            with ZipFile(base/"ejemplo.zip", "w") as z:
                for nombre, contenido in tablas.items():
                    z.writestr(nombre+".txt", contenido.encode("utf-8"))
            resumen = convertir(base/"ejemplo.zip", base/"datos", date(2021,7,14), True)
            self.assertEqual(resumen["horarios"], 2)
            self.assertEqual((base/"datos/horarios.csv").read_text("utf-8").splitlines()[1:],
                             ["R-X-1,SAN MATEO,04:03", "R-X-1,PORTAL SUR,04:10"])
