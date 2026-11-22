"""Árbol AVL propio con inserción, eliminación e iteración ordenada."""


class _Nodo:
    def __init__(self, clave, valor):
        self.clave = clave
        self.valor = valor
        self.izquierda = None
        self.derecha = None
        self.altura = 1


def _altura(nodo):
    return 0 if nodo is None else nodo.altura


def _actualizar(nodo):
    izquierda, derecha = _altura(nodo.izquierda), _altura(nodo.derecha)
    nodo.altura = 1 + (izquierda if izquierda > derecha else derecha)


def _rotar_derecha(nodo):
    nueva = nodo.izquierda
    nodo.izquierda = nueva.derecha
    nueva.derecha = nodo
    _actualizar(nodo)
    _actualizar(nueva)
    return nueva


def _rotar_izquierda(nodo):
    nueva = nodo.derecha
    nodo.derecha = nueva.izquierda
    nueva.izquierda = nodo
    _actualizar(nodo)
    _actualizar(nueva)
    return nueva


def _equilibrar(nodo):
    _actualizar(nodo)
    balance = _altura(nodo.izquierda) - _altura(nodo.derecha)
    if balance > 1:
        hijo = nodo.izquierda
        if _altura(hijo.izquierda) < _altura(hijo.derecha):
            nodo.izquierda = _rotar_izquierda(hijo)
        return _rotar_derecha(nodo)
    if balance < -1:
        hijo = nodo.derecha
        if _altura(hijo.derecha) < _altura(hijo.izquierda):
            nodo.derecha = _rotar_derecha(hijo)
        return _rotar_izquierda(nodo)
    return nodo


def _guardar(nodo, clave, valor):
    if nodo is None:
        return _Nodo(clave, valor)
    if clave < nodo.clave:
        nodo.izquierda = _guardar(nodo.izquierda, clave, valor)
    elif clave > nodo.clave:
        nodo.derecha = _guardar(nodo.derecha, clave, valor)
    else:
        nodo.valor = valor
        return nodo
    return _equilibrar(nodo)


def _eliminar(nodo, clave):
    if nodo is None:
        return None
    if clave < nodo.clave:
        nodo.izquierda = _eliminar(nodo.izquierda, clave)
    elif clave > nodo.clave:
        nodo.derecha = _eliminar(nodo.derecha, clave)
    else:
        if nodo.izquierda is None:
            return nodo.derecha
        if nodo.derecha is None:
            return nodo.izquierda
        sucesor = nodo.derecha
        while sucesor.izquierda is not None:
            sucesor = sucesor.izquierda
        nodo.clave, nodo.valor = sucesor.clave, sucesor.valor
        nodo.derecha = _eliminar(nodo.derecha, sucesor.clave)
    return _equilibrar(nodo)


def _iterar(nodo, desde, hasta):
    pila = []
    actual = nodo
    while actual is not None or pila:
        while actual is not None:
            if desde is not None and actual.clave < desde:
                actual = actual.derecha
            else:
                pila.append(actual)
                actual = actual.izquierda
        if not pila:
            return
        actual = pila.pop()
        if hasta is not None and actual.clave > hasta:
            return
        yield actual.clave, actual.valor
        actual = actual.derecha


def _construir(pares, inicio, fin):
    if inicio >= fin:
        return None
    medio = (inicio + fin) // 2
    clave, valor = pares[medio]
    nodo = _Nodo(clave, valor)
    nodo.izquierda = _construir(pares, inicio, medio)
    nodo.derecha = _construir(pares, medio + 1, fin)
    _actualizar(nodo)
    return nodo


class ArbolOrdenado:
    def __init__(self, pares_ordenados=None):
        pares = [] if pares_ordenados is None else pares_ordenados
        self._raiz = _construir(pares, 0, len(pares))

    def guardar(self, clave, valor):
        self._raiz = _guardar(self._raiz, clave, valor)

    def eliminar(self, clave):
        self._raiz = _eliminar(self._raiz, clave)

    def iterar(self, desde=None, hasta=None):
        return _iterar(self._raiz, desde, hasta)
