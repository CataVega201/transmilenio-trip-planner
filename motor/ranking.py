"""R6. Ranking incremental de estaciones abiertas con un AVL propio."""
from .arbol_ordenado import ArbolOrdenado
from .estaciones import _normalizar
from .indice_alfabetico import _ordenar
from .tabla_hash import TablaHash


class IndiceRanking:
    def __init__(self, filas):
        self._registros = TablaHash()
        pares = []
        for nombre, cantidad in filas:
            clave = _normalizar(nombre)
            self._registros.guardar(clave, [nombre, cantidad, True])
            pares.append(((-cantidad, clave), (nombre, cantidad)))
        self._orden = ArbolOrdenado(_ordenar(pares))

    def actualizar_estacion(self, nombre, cantidad, abierta):
        clave = _normalizar(nombre)
        registro = self._registros.obtener(clave)
        if registro is None:
            raise ValueError("estación inexistente en ranking")
        if registro[2]:
            self._orden.eliminar((-registro[1], clave))
        registro[1], registro[2] = cantidad, abierta
        if abierta:
            self._orden.guardar((-cantidad, clave), (registro[0], cantidad))

    def ranking(self, k):
        if isinstance(k, bool) or not isinstance(k, int):
            raise TypeError("k debe ser entero")
        if k <= 0:
            return []
        resultado = []
        for _, par in self._orden.iterar():
            resultado.append(par)
            if len(resultado) == k:
                break
        return resultado
