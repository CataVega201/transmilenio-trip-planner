"""Carga validada de CSV con tablas hash y ordenamiento propios."""
import csv

from .estaciones import _normalizar
from .horarios import hora_a_minutos
from .tabla_hash import TablaHash


def ordenar(filas):
    """Merge sort iterativo. O(n log n) tiempo y O(n) espacio auxiliar."""
    origen = list(filas)
    destino = [None] * len(origen)
    ancho = 1
    while ancho < len(origen):
        for inicio in range(0, len(origen), 2 * ancho):
            medio = inicio + ancho
            if medio > len(origen):
                medio = len(origen)
            fin = inicio + 2 * ancho
            if fin > len(origen):
                fin = len(origen)
            izquierda, derecha = inicio, medio
            for posicion in range(inicio, fin):
                if izquierda < medio and (
                    derecha >= fin or origen[izquierda] <= origen[derecha]
                ):
                    destino[posicion] = origen[izquierda]
                    izquierda += 1
                else:
                    destino[posicion] = origen[derecha]
                    derecha += 1
        origen, destino = destino, origen
        ancho *= 2
    return origen


def _filas(carpeta, archivo, encabezado):
    ruta = carpeta.rstrip("/\\") + "/" + archivo
    with open(ruta, encoding="utf-8-sig", newline="") as fuente:
        lector = csv.reader(fuente)
        if next(lector, None) != encabezado:
            raise ValueError(archivo + ": encabezado incorrecto")
        for numero, fila in enumerate(lector, 2):
            if len(fila) != len(encabezado):
                raise ValueError(f"{archivo}:{numero}: cantidad de columnas incorrecta")
            yield numero, fila


def _nombre(texto, archivo, numero):
    if not texto.strip():
        raise ValueError(f"{archivo}:{numero}: nombre vacío")
    return _normalizar(texto)


class DatosRed:
    """Nombres originales, recorridos ordenados y eventos sin deduplicar."""

    def __init__(self, carpeta):
        if not isinstance(carpeta, str):
            raise TypeError("carpeta debe ser texto")
        self.estaciones = []
        self.por_estacion = TablaHash()
        self.por_ruta = TablaHash()
        self.rutas = []
        self.horarios = []
        for numero, fila in _filas(carpeta, "estaciones.csv", ["nombre"]):
            nombre = fila[0]
            clave = _nombre(nombre, "estaciones.csv", numero)
            if self.por_estacion.obtener(clave) is not None:
                raise ValueError(f"estaciones.csv:{numero}: estación duplicada o ambigua")
            self.por_estacion.guardar(clave, nombre)
            self.estaciones.append(nombre)

        filas_rutas = []
        for numero, fila in _filas(carpeta, "rutas.csv", ["ruta", "orden", "estacion"]):
            ruta, orden, estacion = fila
            clave = _nombre(ruta, "rutas.csv", numero)
            original = self.por_ruta.obtener(clave)
            if original is not None and original != ruta:
                raise ValueError(f"rutas.csv:{numero}: nombre de ruta ambiguo")
            self.por_ruta.guardar(clave, ruta)
            nombre = self.por_estacion.obtener(_normalizar(estacion))
            if nombre is None:
                raise ValueError(f"rutas.csv:{numero}: estación inexistente")
            if not orden.isascii() or not orden.isdigit() or int(orden) <= 0:
                raise ValueError(f"rutas.csv:{numero}: orden inválido")
            filas_rutas.append((ruta, int(orden), nombre, numero))

        parejas = TablaHash()
        ruta_anterior, orden_anterior = None, None
        for ruta, orden, nombre, numero in ordenar(filas_rutas):
            if ruta == ruta_anterior and orden == orden_anterior:
                raise ValueError(f"rutas.csv:{numero}: orden duplicado")
            clave = (ruta, nombre)
            if parejas.obtener(clave, False):
                raise ValueError(f"rutas.csv:{numero}: estación repetida en la ruta")
            parejas.guardar(clave, True)
            self.rutas.append((ruta, nombre))
            ruta_anterior, orden_anterior = ruta, orden

        for numero, fila in _filas(carpeta, "horarios.csv", ["ruta", "estacion", "hora"]):
            ruta, estacion, hora = fila
            original = self.por_ruta.obtener(_normalizar(ruta))
            nombre = self.por_estacion.obtener(_normalizar(estacion))
            if original is None or nombre is None or not parejas.obtener((original, nombre), False):
                raise ValueError(f"horarios.csv:{numero}: pareja ruta-estación inexistente")
            try:
                hora_a_minutos(hora)
            except (ValueError, TypeError) as error:
                raise ValueError(f"horarios.csv:{numero}: hora inválida") from error
            self.horarios.append((original, nombre, hora))
