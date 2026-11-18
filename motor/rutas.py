"""R7 - Recorridos y edicion de rutas.

Cada ruta representa UN sentido y se guarda como lista doblemente enlazada de
paradas. Asi se recorre en ambos sentidos sin copiar ni invertir, y agregar o
quitar una parada solo cambia los enlaces de sus vecinas.

Localizar una parada por nombre es un costo aparte del cambio de enlaces:
- con una fabrica de tablas (la TablaHash de Mariana) cada ruta mantiene un
  indice estacion -> nodo y localizar cuesta O(1) esperado;
- sin fabrica se recorre la lista: O(L), con L paradas en la ruta.

Este modulo no crea su propia tabla hash: recibe la fabrica desde fuera.
No usa dict, set, sorted, min/max sobre colecciones, `in` sobre listas,
.index() ni .count().
"""


class NodoParada:
    """Una parada dentro de una ruta. Campos: estacion, anterior, siguiente."""

    def __init__(self, estacion):
        self.estacion = estacion
        self.anterior = None
        self.siguiente = None


class Ruta:
    """Lista doblemente enlazada de paradas, sin estaciones repetidas.

    Invariantes tras cada operacion:
    - cabeza.anterior es None y cola.siguiente es None;
    - para todo nodo con siguiente, nodo.siguiente.anterior es nodo;
    - ruta vacia: cabeza y cola son None y la cantidad es 0;
    - si hay indice, contiene exactamente las estaciones enlazadas.
    """

    def __init__(self, nombre, crear_tabla=None):
        self.nombre = nombre
        self._cabeza = None
        self._cola = None
        self._cantidad = 0
        self._indice = None if crear_tabla is None else crear_tabla()

    def __len__(self):
        return self._cantidad

    def primera(self):
        """Primer nodo del recorrido, o None si la ruta esta vacia."""
        return self._cabeza

    def ultima(self):
        """Ultimo nodo del recorrido, o None si la ruta esta vacia."""
        return self._cola

    def nodo(self, estacion):
        """Nodo de la estacion o None. O(1) esperado con indice; O(L) sin el."""
        if self._indice is not None:
            return self._indice.obtener(estacion)
        actual = self._cabeza
        while actual is not None:
            if actual.estacion == estacion:
                return actual
            actual = actual.siguiente
        return None

    def contiene(self, estacion):
        return self.nodo(estacion) is not None

    def anterior_de(self, estacion):
        """Nombre de la parada previa; None si es la primera o no esta."""
        nodo = self.nodo(estacion)
        if nodo is None or nodo.anterior is None:
            return None
        return nodo.anterior.estacion

    def _registrar(self, nodo):
        self._cantidad += 1
        if self._indice is not None:
            self._indice.guardar(nodo.estacion, nodo)

    def agregar_al_final(self, estacion):
        """Agrega la parada como ultima. False si ya estaba. Enlaces en O(1)."""
        if self.contiene(estacion):
            return False
        nodo = NodoParada(estacion)
        if self._cola is None:
            self._cabeza = nodo
        else:
            nodo.anterior = self._cola
            self._cola.siguiente = nodo
        self._cola = nodo
        self._registrar(nodo)
        return True

    def insertar_al_inicio(self, estacion):
        """Agrega la parada como primera. False si ya estaba.

        No es una operacion publica de Red: la usa deshacer para devolver a
        su sitio una parada que era la primera de la ruta.
        """
        if self.contiene(estacion):
            return False
        nodo = NodoParada(estacion)
        if self._cabeza is None:
            self._cola = nodo
        else:
            nodo.siguiente = self._cabeza
            self._cabeza.anterior = nodo
        self._cabeza = nodo
        self._registrar(nodo)
        return True

    def insertar_despues(self, nueva, despues_de):
        """Inserta `nueva` justo despues de `despues_de`.

        False si `nueva` ya esta en la ruta o `despues_de` no esta. En una ruta
        vacia siempre es False porque no existe la parada de referencia.
        """
        referencia = self.nodo(despues_de)
        if referencia is None or self.contiene(nueva):
            return False
        nodo = NodoParada(nueva)
        siguiente = referencia.siguiente
        nodo.anterior = referencia
        nodo.siguiente = siguiente
        referencia.siguiente = nodo
        if siguiente is None:
            self._cola = nodo
        else:
            siguiente.anterior = nodo
        self._registrar(nodo)
        return True

    def quitar(self, estacion):
        """Desenlaza la parada. False si no estaba. Enlaces en O(1)."""
        nodo = self.nodo(estacion)
        if nodo is None:
            return False
        anterior = nodo.anterior
        siguiente = nodo.siguiente
        if anterior is None:
            self._cabeza = siguiente
        else:
            anterior.siguiente = siguiente
        if siguiente is None:
            self._cola = anterior
        else:
            siguiente.anterior = anterior
        nodo.anterior = None
        nodo.siguiente = None
        self._cantidad -= 1
        if self._indice is not None:
            self._indice.eliminar(estacion)
        return True

    def recorrido(self, al_reves=False):
        """Lista nueva con los nombres en orden. O(L). No modifica la ruta."""
        nombres = []
        if al_reves:
            actual = self._cola
            while actual is not None:
                nombres.append(actual.estacion)
                actual = actual.anterior
        else:
            actual = self._cabeza
            while actual is not None:
                nombres.append(actual.estacion)
                actual = actual.siguiente
        return nombres


class AlmacenRutas:
    """Todas las rutas de la red y la pertenencia vigente estacion -> rutas.

    Es el adaptador que consultan viajes, horarios y ranking para saber que
    rutas pasan HOY por una estacion, despues de cualquier edicion.

    Con fabrica de tablas: buscar una ruta y las rutas de una estacion cuesta
    O(1) esperado. Sin fabrica se recorren las rutas (solo para pruebas
    pequenas de este modulo).
    """

    def __init__(self, crear_tabla=None):
        self._crear_tabla = crear_tabla
        self._rutas = []
        self._por_nombre = None
        self._por_estacion = None
        if crear_tabla is not None:
            self._por_nombre = crear_tabla()
            self._por_estacion = crear_tabla()

    def __len__(self):
        return len(self._rutas)

    def obtener(self, nombre):
        """Objeto Ruta o None si no existe."""
        if self._por_nombre is not None:
            return self._por_nombre.obtener(nombre)
        for ruta in self._rutas:
            if ruta.nombre == nombre:
                return ruta
        return None

    def crear(self, nombre):
        """Devuelve la ruta con ese nombre, creandola vacia si no existia."""
        ruta = self.obtener(nombre)
        if ruta is None:
            ruta = Ruta(nombre, self._crear_tabla)
            self._rutas.append(ruta)
            if self._por_nombre is not None:
                self._por_nombre.guardar(nombre, ruta)
        return ruta

    def nombres(self):
        """Nombres de las rutas en orden de creacion."""
        nombres = []
        for ruta in self._rutas:
            nombres.append(ruta.nombre)
        return nombres

    def rutas_de(self, estacion):
        """Nombres de las rutas cuyo recorrido vigente incluye la estacion."""
        resultado = []
        if self._por_estacion is not None:
            guardadas = self._por_estacion.obtener(estacion)
            if guardadas is not None:
                for nombre in guardadas:
                    resultado.append(nombre)
            return resultado
        for ruta in self._rutas:
            if ruta.contiene(estacion):
                resultado.append(ruta.nombre)
        return resultado

    def _anotar(self, estacion, nombre_ruta):
        if self._por_estacion is None:
            return
        guardadas = self._por_estacion.obtener(estacion)
        if guardadas is None:
            guardadas = []
            self._por_estacion.guardar(estacion, guardadas)
        guardadas.append(nombre_ruta)

    def _borrar(self, estacion, nombre_ruta):
        if self._por_estacion is None:
            return
        guardadas = self._por_estacion.obtener(estacion)
        if guardadas is None:
            return
        restantes = []
        for nombre in guardadas:
            if nombre != nombre_ruta:
                restantes.append(nombre)
        if len(restantes) == 0:
            self._por_estacion.eliminar(estacion)
        else:
            self._por_estacion.guardar(estacion, restantes)

    def agregar_al_final(self, ruta, estacion):
        """Usado en la carga: crea la ruta si hace falta y agrega la parada."""
        if not self.crear(ruta).agregar_al_final(estacion):
            return False
        self._anotar(estacion, ruta)
        return True

    def agregar_parada(self, ruta, nueva, despues_de):
        """R7. True si la ruta cambia. No crea rutas ni comprueba que la
        estacion exista en la red: eso lo decide Red antes de llamar."""
        objeto = self.obtener(ruta)
        if objeto is None or not objeto.insertar_despues(nueva, despues_de):
            return False
        self._anotar(nueva, ruta)
        return True

    def insertar_al_inicio(self, ruta, estacion):
        """Solo para deshacer/rehacer una parada que era la primera."""
        objeto = self.obtener(ruta)
        if objeto is None or not objeto.insertar_al_inicio(estacion):
            return False
        self._anotar(estacion, ruta)
        return True

    def quitar_parada(self, ruta, estacion):
        """R7. True si quita una parada existente; la ruta puede quedar vacia."""
        objeto = self.obtener(ruta)
        if objeto is None or not objeto.quitar(estacion):
            return False
        self._borrar(estacion, ruta)
        return True

    def recorrido(self, ruta, al_reves=False):
        """R7. Lista de nombres, o [] si la ruta no existe o esta vacia."""
        objeto = self.obtener(ruta)
        if objeto is None:
            return []
        return objeto.recorrido(al_reves)
