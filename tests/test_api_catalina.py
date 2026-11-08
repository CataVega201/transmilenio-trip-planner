import unittest
from unittest.mock import Mock
from servidor import crear_app


class ContratoWeb(unittest.TestCase):
    def setUp(self):
        self.red = Mock()
        self.cliente = crear_app(red=self.red).test_client()

    def test_lecturas_y_operaciones(self):
        casos = [
            ('estaciones/estado', 'estado', {'nombre':'A'}, ('A',)),
            ('estaciones/autocompletar', 'autocompletar', {'prefijo':'A','k':'5'}, ('A',5)),
            ('estaciones/rango', 'rango', {'desde':'A','hasta':'C'}, ('A','C')),
            ('horarios/proximo', 'proximo_bus', {'ruta':'R','estacion':'A','hora':'25:10'}, ('A','R','25:10')),
            ('viajes', 'viaje', {'origen':'A','destino':'B'}, ('A','B')),
            ('ranking', 'ranking', {'k':'2'}, (2,)),
            ('rutas/recorrido', 'recorrido', {'ruta':'R','al_reves':'false'}, ('R',False)),
        ]
        for ruta, metodo, campos, argumentos in casos:
            with self.subTest(ruta=ruta):
                getattr(self.red, metodo).return_value = None
                respuesta = self.cliente.get('/api/'+ruta, query_string=campos)
                self.assertEqual(respuesta.json, {'ok':True,'datos':None})
                getattr(self.red, metodo).assert_called_once_with(*argumentos)
        cambios = [
            ('estaciones/cerrar','cerrar',{'nombre':'A'},('A',)),
            ('estaciones/reabrir','reabrir',{'nombre':'A'},('A',)),
            ('rutas/agregar','agregar_parada',{'ruta':'R','nueva':'B','despues_de':'A'},('R','B','A')),
            ('rutas/quitar','quitar_parada',{'ruta':'R','estacion':'B'},('R','B')),
            ('historial/deshacer','deshacer',{},()),
            ('historial/rehacer','rehacer',{},()),
        ]
        for ruta, metodo, campos, argumentos in cambios:
            with self.subTest(ruta=ruta):
                getattr(self.red, metodo).return_value = False
                respuesta = self.cliente.post('/api/'+ruta,json=campos)
                self.assertEqual(respuesta.json, {'ok':True,'datos':False})
                getattr(self.red, metodo).assert_called_once_with(*argumentos)

    def test_entradas_invalidas(self):
        for ruta in ['/api/estaciones/estado','/api/ranking?k=no','/api/rutas/recorrido?ruta=A&al_reves=no']:
            self.assertEqual(self.cliente.get(ruta).status_code, 400)
        self.assertEqual(self.cliente.post('/api/estaciones/cerrar',json=[]).status_code,400)

    def test_salud_y_modulos_inyectados(self):
        fila, medir = Mock(return_value=[]), Mock(return_value=[])
        cliente = crear_app(simular=fila, medir=medir).test_client()
        self.assertEqual(cliente.get('/api/estado').json['estado'],'ok')
        self.assertTrue(cliente.post('/api/fila',json={'llegadas':[0],'frecuencia':5,'capacidad':2}).json['ok'])
        fila.assert_called_once_with([0],5,2)
        self.assertTrue(cliente.post('/api/rendimiento',json={'tamanos':[100],'repeticiones':3}).json['ok'])
        medir.assert_called_once_with([100],3)
        self.assertEqual(self.cliente.post('/api/rendimiento',json={}).status_code,503)

