"""R9 - Historial de deshacer y rehacer con dos pilas propias.

El historial no sabe aplicar cambios: solo guarda acciones (registros que arma
Red con los datos justos para invertir el cambio exacto) y decide cual toca.
Red aplica la inversa SIN volver a registrar, para no duplicar acciones.

Reglas (docs/CONTRATOS.md):
- se registra solo un cambio exitoso; registrar vacia la pila de rehacer;
- deshacer mueve la accion mas reciente a la pila de rehacer;
- rehacer la devuelve a la pila de deshacer;
- ninguna de las dos operaciones crea acciones nuevas.

No usa dict, set, collections ni otras estructuras prohibidas.
"""


class _Nodo:
    """Eslabon de la pila. Campos: valor, debajo."""

    def __init__(self, valor, debajo):
        self.valor = valor
        self.debajo = debajo


class Pila:
    """Pila LIFO enlazada. apilar, desapilar, cima y vaciar en O(1) peor caso."""

    def __init__(self):
        self._cima = None
        self._cantidad = 0

    def __len__(self):
        return self._cantidad

    def vacia(self):
        return self._cima is None

    def apilar(self, valor):
        self._cima = _Nodo(valor, self._cima)
        self._cantidad += 1

    def desapilar(self):
        """Saca y devuelve el valor mas reciente; None si esta vacia."""
        nodo = self._cima
        if nodo is None:
            return None
        self._cima = nodo.debajo
        self._cantidad -= 1
        return nodo.valor

    def cima(self):
        """Valor mas reciente sin sacarlo; None si esta vacia."""
        if self._cima is None:
            return None
        return self._cima.valor

    def vaciar(self):
        """Suelta toda la cadena de una vez: O(1), sin recorrerla."""
        self._cima = None
        self._cantidad = 0


class Historial:
    """Dos pilas: acciones por deshacer y acciones por rehacer."""

    def __init__(self):
        self._hechas = Pila()
        self._deshechas = Pila()

    def registrar(self, accion):
        """Anota un cambio exitoso nuevo y descarta lo que se podia rehacer."""
        self._hechas.apilar(accion)
        self._deshechas.vaciar()

    def deshacer(self):
        """Devuelve la accion que Red debe invertir, o None si no hay."""
        if self._hechas.vacia():
            return None
        accion = self._hechas.desapilar()
        self._deshechas.apilar(accion)
        return accion

    def rehacer(self):
        """Devuelve la accion que Red debe volver a aplicar, o None."""
        if self._deshechas.vacia():
            return None
        accion = self._deshechas.desapilar()
        self._hechas.apilar(accion)
        return accion

    def puede_deshacer(self):
        return not self._hechas.vacia()

    def puede_rehacer(self):
        return not self._deshechas.vacia()

    def pendientes(self):
        """Par [por_deshacer, por_rehacer] para pruebas y mediciones."""
        return [len(self._hechas), len(self._deshechas)]
