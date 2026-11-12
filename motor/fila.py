"""R10 - Simulacion de la fila de abordaje.

Funcion publica: simular_fila(llegadas, frecuencia, capacidad).

Reglas acordadas (docs/CONTRATOS.md, seccion 4):
- llegadas: lista de minutos enteros no negativos en orden no decreciente.
  Cada elemento es una persona; puede haber varias en el mismo minuto.
- frecuencia y capacidad: enteros positivos (los bool no cuentan).
- El primer bus sale en el minuto 0 y los demas en multiplos de frecuencia.
- Quien llega en el mismo minuto que un bus puede abordarlo
  (llegada antes de salida en el mismo instante).
- Se respeta FIFO; si el bus se llena, los demas esperan el siguiente.
- Respuesta: lista de registros [llegada, abordaje, espera], uno por
  pasajero, en orden de entrada. espera = abordaje - llegada.

Solo usa estructuras propias: no dict, set, collections, sorted, etc.
"""


class ColaFIFO:
    """Cola FIFO sobre un arreglo circular con crecimiento amortizado.

    Campos:
    - _datos: arreglo (lista de tamano fijo) con los elementos.
    - _inicio: posicion del primer elemento (el proximo en salir).
    - _tamano: cantidad de elementos guardados.

    encolar y desencolar cuestan O(1) amortizado: solo cuando el arreglo
    se llena se copia a uno del doble de tamano (O(tamano) esa vez).
    """

    def __init__(self, capacidad_inicial=8):
        if capacidad_inicial < 1:
            capacidad_inicial = 1
        self._datos = [None] * capacidad_inicial
        self._inicio = 0
        self._tamano = 0

    def vacia(self):
        return self._tamano == 0

    def __len__(self):
        return self._tamano

    def encolar(self, valor):
        if self._tamano == len(self._datos):
            self._crecer()
        fin = (self._inicio + self._tamano) % len(self._datos)
        self._datos[fin] = valor
        self._tamano += 1

    def desencolar(self):
        if self._tamano == 0:
            raise IndexError("La cola esta vacia")
        valor = self._datos[self._inicio]
        self._datos[self._inicio] = None  # libera la referencia
        self._inicio = (self._inicio + 1) % len(self._datos)
        self._tamano -= 1
        return valor

    def frente(self):
        if self._tamano == 0:
            raise IndexError("La cola esta vacia")
        return self._datos[self._inicio]

    def _crecer(self):
        viejo = self._datos
        capacidad = len(viejo)
        nuevo = [None] * (capacidad * 2)
        # Copia en orden FIFO: el primero queda en la posicion 0.
        for j in range(self._tamano):
            nuevo[j] = viejo[(self._inicio + j) % capacidad]
        self._datos = nuevo
        self._inicio = 0


def _es_entero(valor):
    # bool es subclase de int en Python, pero no cuenta como entero aqui.
    return isinstance(valor, int) and not isinstance(valor, bool)


def _validar(llegadas, frecuencia, capacidad):
    if not isinstance(llegadas, (list, tuple)):
        raise TypeError("llegadas debe ser una lista de minutos enteros")
    if not _es_entero(frecuencia):
        raise TypeError("frecuencia debe ser un entero")
    if not _es_entero(capacidad):
        raise TypeError("capacidad debe ser un entero")
    if frecuencia <= 0:
        raise ValueError("frecuencia debe ser mayor que cero")
    if capacidad <= 0:
        raise ValueError("capacidad debe ser mayor que cero")

    anterior = 0
    for posicion in range(len(llegadas)):
        minuto = llegadas[posicion]
        if not _es_entero(minuto):
            raise TypeError(
                "la llegada en la posicion %d no es un entero" % posicion)
        if minuto < 0:
            raise ValueError(
                "la llegada en la posicion %d es negativa" % posicion)
        if minuto < anterior:
            raise ValueError(
                "las llegadas deben estar en orden no decreciente "
                "(posicion %d)" % posicion)
        anterior = minuto


def _primer_bus_desde(minuto, frecuencia):
    """Menor multiplo de frecuencia que es mayor o igual a minuto."""
    return ((minuto + frecuencia - 1) // frecuencia) * frecuencia


def simular_fila(llegadas, frecuencia, capacidad):
    """Simula la fila de abordaje avanzando solo entre eventos utiles.

    Ejemplo:
    >>> simular_fila([0, 0, 1, 10], 10, 2)
    [[0, 0, 0], [0, 0, 0], [1, 10, 9], [10, 10, 0]]
    """
    _validar(llegadas, frecuencia, capacidad)

    n = len(llegadas)
    resultado = []
    cola = ColaFIFO()
    siguiente = 0   # indice de la proxima persona que aun no llega a la fila
    bus = 0         # minuto del proximo bus a considerar

    while siguiente < n or not cola.vacia():
        # Salto de tiempo: si nadie espera, el proximo bus util es el primero
        # que sale en o despues de la siguiente llegada. No se recorren
        # minutos ni buses vacios.
        if cola.vacia():
            llegada = llegadas[siguiente]
            if bus < llegada:
                bus = _primer_bus_desde(llegada, frecuencia)

        # Llegadas antes de salida: entran a la fila todos los que llegan
        # hasta el minuto del bus, incluido ese mismo minuto.
        while siguiente < n and llegadas[siguiente] <= bus:
            cola.encolar(llegadas[siguiente])
            siguiente += 1

        # El bus sale: suben en orden FIFO hasta llenar la capacidad.
        subieron = 0
        while subieron < capacidad and not cola.vacia():
            llegada = cola.desencolar()
            resultado.append([llegada, bus, bus - llegada])
            subieron += 1

        bus += frecuencia

    return resultado
