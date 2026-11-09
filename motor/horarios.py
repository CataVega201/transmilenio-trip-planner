"""Funciones de horarios de R4, sin dependencias externas."""


def hora_a_minutos(hora):
    """Convierte HH:MM a minutos del dia de servicio, admitiendo 24:00 y mas.

    Exige al menos dos digitos de horas y exactamente dos de minutos.
    No aplica modulo 24: 25:10 representa 1510 minutos, no 70.
    """
    if not isinstance(hora, str):
        raise TypeError("La hora debe ser un texto en formato HH:MM")

    if len(hora) < 5 or hora[-3] != ":":
        raise ValueError("La hora debe tener formato HH:MM")

    horas = hora[:-3]
    minutos = hora[-2:]
    for digito in horas + minutos:
        if digito < "0" or digito > "9":
            raise ValueError("La hora solo admite digitos y el separador ':'")

    valor_minutos = int(minutos)
    if valor_minutos > 59:
        raise ValueError("Los minutos deben estar entre 00 y 59")

    return int(horas) * 60 + valor_minutos


def _ordenar_horarios(horarios):
    """Ordena minutos en el mismo arreglo conservando todos los eventos.

    Merge sort iterativo: O(h log h) tiempo y O(h) memoria auxiliar.
    Solo se utiliza al preparar el indice, no durante cada consulta.
    """
    cantidad = len(horarios)
    if cantidad < 2:
        return

    auxiliar = [0] * cantidad
    origen = horarios
    destino = auxiliar
    ancho = 1
    while ancho < cantidad:
        inicio = 0
        while inicio < cantidad:
            medio = inicio + ancho
            if medio > cantidad:
                medio = cantidad
            fin = inicio + 2 * ancho
            if fin > cantidad:
                fin = cantidad
            izquierda = inicio
            derecha = medio
            posicion = inicio
            while posicion < fin:
                if izquierda < medio and (
                    derecha >= fin or origen[izquierda] <= origen[derecha]
                ):
                    destino[posicion] = origen[izquierda]
                    izquierda += 1
                else:
                    destino[posicion] = origen[derecha]
                    derecha += 1
                posicion += 1
            inicio = fin
        origen, destino = destino, origen
        ancho *= 2

    if origen is not horarios:
        for posicion in range(cantidad):
            horarios[posicion] = origen[posicion]


def _buscar_siguiente(horarios, minuto):
    """Devuelve el primer minuto >= minuto, o None si no existe.

    Ayudante interno: recibe minutos ya validados y un arreglo ordenado de
    menor a mayor. El indice prepara ese arreglo una sola vez al cargarlo.
    No lo ordenamos ni copiamos en cada consulta: tiempo O(log h) y espacio
    auxiliar O(1), donde h es la cantidad de horarios del arreglo.
    """
    izquierda = 0
    derecha = len(horarios)

    # Antes de izquierda todos son menores; desde derecha ninguno lo es.
    while izquierda < derecha:
        medio = (izquierda + derecha) // 2
        if horarios[medio] < minuto:
            izquierda = medio + 1
        else:
            derecha = medio

    if izquierda == len(horarios):
        return None
    return horarios[izquierda]


class IndiceHorarios:
    """Índice por estación y ruta; los nombres llegan normalizados desde Red."""

    def __init__(self, filas, *, crear_tabla=None):
        if crear_tabla is None:
            from .tabla_hash import TablaHash
            crear_tabla = TablaHash
        self._estaciones = crear_tabla()
        grupos = []
        for ruta, estacion, hora in filas:
            rutas = self._estaciones.obtener(estacion)
            if rutas is None:
                rutas = crear_tabla()
                self._estaciones.guardar(estacion, rutas)
            horarios = rutas.obtener(ruta)
            if horarios is None:
                horarios = []
                rutas.guardar(ruta, horarios)
                grupos.append(horarios)
            horarios.append(hora_a_minutos(hora))
        for horarios in grupos:
            _ordenar_horarios(horarios)

    def _horarios(self, estacion, ruta):
        rutas = self._estaciones.obtener(estacion)
        if rutas is None:
            return None
        return rutas.obtener(ruta)

    def siguiente(self, estacion, ruta, hora):
        minuto = hora_a_minutos(hora)
        horarios = self._horarios(estacion, ruta)
        if horarios is None:
            return None
        bus = _buscar_siguiente(horarios, minuto)
        if bus is None:
            return None
        return f"{bus // 60:02d}:{bus % 60:02d}"

    def cantidad(self, estacion, ruta):
        horarios = self._horarios(estacion, ruta)
        return 0 if horarios is None else len(horarios)
