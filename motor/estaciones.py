"""Índice de estaciones: estado abierto/cerrado de cada una."""

from motor.tabla_hash import TablaHash


def _normalizar(nombre):
    texto = nombre.strip().upper()
    texto = texto.replace("Á", "A")
    texto = texto.replace("É", "E")
    texto = texto.replace("Í", "I")
    texto = texto.replace("Ó", "O")
    texto = texto.replace("Ú", "U")
    texto = texto.replace("Ü", "U")
    return texto


class _Estacion:
    def __init__(self, nombre):
        self.nombre = nombre
        self.abierta = True


class IndiceEstaciones:
    def __init__(self, nombres):
        self._tabla = TablaHash()
        for nombre in nombres:
            clave = _normalizar(nombre)
            self._tabla.guardar(clave, _Estacion(nombre))

    def estado(self, nombre):
        registro = self._tabla.obtener(_normalizar(nombre))
        if registro is None:
            return "NO EXISTE"
        if registro.abierta:
            return "ABIERTA"
        return "CERRADA"

    def cambiar_estado(self, nombre, abierta):
        registro = self._tabla.obtener(_normalizar(nombre))
        if registro is None:
            return False
        if registro.abierta == abierta:
            return False
        registro.abierta = abierta
        return True
    
