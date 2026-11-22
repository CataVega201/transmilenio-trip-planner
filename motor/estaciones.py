from motor.indice_alfabetico import _ordenar, _primer_indice
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

def _validar_texto(valor, nombre):
    if not isinstance(valor, str):
        raise TypeError(f"{nombre} debe ser texto")
    
class _Estacion:
    def __init__(self, nombre):
        self.nombre = nombre
        self.abierta = True


class IndiceEstaciones:
    def __init__(self, nombres):
        self._tabla = TablaHash()
        claves = []
        for nombre in nombres:
            clave = _normalizar(nombre)
            if self._tabla.obtener(clave) is None:
                claves.append(clave)
            self._tabla.guardar(clave, _Estacion(nombre))
        self._claves = _ordenar(claves)

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
    
    def autocompletar(self, prefijo, k):
        
        _validar_texto(prefijo, "prefijo")
        if isinstance(k, bool) or not isinstance(k, int):
            raise TypeError("k debe ser un entero")
        if k <= 0:
            return []
        prefijo = _normalizar(prefijo)
        resultados = []
        i = _primer_indice(self._claves, prefijo)
        while i < len(self._claves) and len(resultados) < k:
            clave = self._claves[i]
            if not clave.startswith(prefijo):
                break
            registro = self._tabla.obtener(clave)
            if registro.abierta:
                resultados.append(registro.nombre)
            i += 1
        return resultados

    