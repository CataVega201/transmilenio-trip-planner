"""R5. Viajes dirigidos con cero o un transbordo y menos paradas."""
from .tabla_hash import TablaHash


def planear_viaje(rutas, estaciones, origen, destino):
    if estaciones.estado(origen) != "ABIERTA" or estaciones.estado(destino) != "ABIERTA":
        return None
    if origen == destino:
        return []

    # Para cada estación guardamos el mejor primer tramo desde el origen.
    primeras = TablaHash()
    for nombre_ruta in rutas.rutas_de(origen):
        nodo = rutas.obtener(nombre_ruta).nodo(origen).siguiente
        distancia = 1
        while nodo is not None:
            if estaciones.estado(nodo.estacion) == "ABIERTA":
                candidato = (distancia, nombre_ruta)
                anterior = primeras.obtener(nodo.estacion)
                if anterior is None or candidato < anterior:
                    primeras.guardar(nodo.estacion, candidato)
            distancia += 1
            nodo = nodo.siguiente

    directo = primeras.obtener(destino)
    mejor = None
    resultado = None
    if directo is not None:
        distancia, ruta = directo
        mejor = (distancia, 0, ruta, "", "")
        resultado = [(ruta, origen, destino)]

    # Se recorren hacia atrás solo las rutas que llegan al destino.
    for segunda in rutas.rutas_de(destino):
        nodo = rutas.obtener(segunda).nodo(destino).anterior
        distancia = 1
        while nodo is not None:
            primero = primeras.obtener(nodo.estacion)
            if primero is not None:
                costo, primera = primero
                candidato = (costo + distancia, 1, primera, segunda, nodo.estacion)
                if mejor is None or candidato < mejor:
                    mejor = candidato
                    resultado = [(primera, origen, nodo.estacion),
                                 (segunda, nodo.estacion, destino)]
            distancia += 1
            nodo = nodo.anterior
    return resultado
