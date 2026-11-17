"""R10 - Simulacion de la fila de abordaje.

Funcion publica: simular_fila(llegadas, frecuencia, capacidad).

Contrato del profesor:
- llegadas: segundos en que llega cada persona.
- frecuencia: segundos entre buses. Los buses salen en frecuencia,
  2*frecuencia, 3*frecuencia, ... (no hay bus en el segundo 0).
- capacidad: cupo de cada bus.
- La gente sube en orden de llegada (FIFO).
- Devuelve, en el mismo orden de la lista llegadas, el segundo en que
  salio el bus de cada persona.

Decisiones del equipo para lo que el contrato no dice:
- Quien llega justo en el segundo en que sale un bus alcanza a subir.
- Si dos personas llegan en el mismo segundo, sube primero la que aparece
  antes en la lista.
- Las llegadas pueden venir desordenadas; se ordenan con un merge sort
  propio. Si ya vienen ordenadas no se paga ese costo.
- Llegadas negativas, frecuencia o capacidad no positivas y tipos no
  numericos (incluido bool) se rechazan con ValueError o TypeError.

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


def _es_numero(valor):
    # bool es subclase de int en Python, pero no cuenta como numero aqui.
    return (isinstance(valor, (int, float)) and not isinstance(valor, bool)
            and valor == valor and valor not in (float("inf"), float("-inf")))


def _validar(llegadas, frecuencia, capacidad):
    """Valida la entrada y dice si las llegadas ya estan ordenadas."""
    if not isinstance(llegadas, (list, tuple)):
        raise TypeError("llegadas debe ser una lista de segundos")
    if not _es_numero(frecuencia):
        raise TypeError("frecuencia debe ser un numero")
    if isinstance(capacidad, bool) or not isinstance(capacidad, int):
        raise TypeError("capacidad debe ser un entero")
    if frecuencia <= 0:
        raise ValueError("frecuencia debe ser mayor que cero")
    if capacidad <= 0:
        raise ValueError("capacidad debe ser mayor que cero")

    ordenadas = True
    for posicion in range(len(llegadas)):
        segundo = llegadas[posicion]
        if not _es_numero(segundo):
            raise TypeError(
                "la llegada en la posicion %d no es un numero" % posicion)
        if segundo < 0:
            raise ValueError(
                "la llegada en la posicion %d es negativa" % posicion)
        if posicion > 0 and segundo < llegadas[posicion - 1]:
            ordenadas = False
    return ordenadas


def _orden_de_llegada(llegadas):
    """Posiciones de llegadas ordenadas por segundo (merge sort estable).

    En empate conserva el orden de la lista original. O(n log n).
    """
    n = len(llegadas)
    actual = list(range(n))
    auxiliar = [0] * n
    ancho = 1
    while ancho < n:
        inicio = 0
        while inicio < n:
            medio = inicio + ancho
            if medio > n:
                medio = n
            fin = inicio + 2 * ancho
            if fin > n:
                fin = n
            i = inicio
            j = medio
            k = inicio
            while i < medio and j < fin:
                # <= mantiene la estabilidad: en empate gana el de la izquierda.
                if llegadas[actual[i]] <= llegadas[actual[j]]:
                    auxiliar[k] = actual[i]
                    i += 1
                else:
                    auxiliar[k] = actual[j]
                    j += 1
                k += 1
            while i < medio:
                auxiliar[k] = actual[i]
                i += 1
                k += 1
            while j < fin:
                auxiliar[k] = actual[j]
                j += 1
                k += 1
            inicio = fin
        actual, auxiliar = auxiliar, actual
        ancho *= 2
    return actual


def _primer_bus_desde(segundo, frecuencia):
    """Primer bus (frecuencia, 2*frecuencia, ...) que sale en o despues de segundo."""
    k = int(segundo // frecuencia)
    if k * frecuencia < segundo:
        k += 1
    if k < 1:
        k = 1  # no hay bus en el segundo 0
    return k * frecuencia


def simular_fila(llegadas, frecuencia, capacidad):
    """Simula la fila de abordaje avanzando solo entre eventos utiles.

    Ejemplo:
    >>> simular_fila([0, 0, 1, 10], 10, 2)
    [10, 10, 20, 20]
    >>> simular_fila([25, 3, 3], 10, 1)
    [30, 10, 20]
    """
    ordenadas = _validar(llegadas, frecuencia, capacidad)

    n = len(llegadas)
    salidas = [0] * n
    if n == 0:
        return []

    if ordenadas:
        orden = range(n)
    else:
        orden = _orden_de_llegada(llegadas)

    cola = ColaFIFO()
    siguiente = 0              # cuantas personas ya entraron a la fila
    bus = frecuencia           # salida del proximo bus a considerar

    while siguiente < n or not cola.vacia():
        # Salto de tiempo: si nadie espera, se va directo al primer bus que
        # sale en o despues de la siguiente llegada. No se recorren buses
        # vacios.
        if cola.vacia():
            llegada = llegadas[orden[siguiente]]
            if bus < llegada:
                bus = _primer_bus_desde(llegada, frecuencia)

        # Llegadas antes de salida: entran a la fila todos los que llegan
        # hasta el segundo del bus, incluido ese mismo segundo.
        while siguiente < n and llegadas[orden[siguiente]] <= bus:
            cola.encolar(orden[siguiente])
            siguiente += 1

        # El bus sale: suben en orden FIFO hasta llenar la capacidad.
        subieron = 0
        while subieron < capacidad and not cola.vacia():
            salidas[cola.desencolar()] = bus
            subieron += 1

        bus += frecuencia

    return salidas
