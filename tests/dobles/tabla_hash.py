"""DOBLE DE PRUEBA de motor/tabla_hash.py (propietaria: Mariana).

Solo imita la interfaz del contrato para probar los modulos de Alejandro
mientras la TablaHash real no este integrada. Usa dict porque esta FUERA de
motor/. No copiar a motor/.
"""


class TablaHash:
    def __init__(self):
        self._datos = {}

    def guardar(self, clave, valor):
        self._datos[clave] = valor

    def obtener(self, clave, defecto=None):
        return self._datos.get(clave, defecto)

    def eliminar(self, clave):
        if clave in self._datos:
            del self._datos[clave]
            return True
        return False

    def pares(self):
        return [[clave, valor] for clave, valor in self._datos.items()]
