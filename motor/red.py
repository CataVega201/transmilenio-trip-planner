"""Fachada pública. Coordina los índices sin duplicar sus algoritmos."""
from .carga import DatosRed
from .estaciones import IndiceEstaciones, _normalizar
from .historial import Historial
from .horarios import IndiceHorarios, hora_a_minutos
from .rutas import AlmacenRutas
from .tabla_hash import TablaHash
from .viajes import planear_viaje


class ModuloPendiente(Exception):
    """Una consulta requiere un índice que aún no está publicado."""


class Red:
    def __init__(self, carpeta):
        datos = DatosRed(carpeta)
        self._nombres = datos.por_estacion
        self._nombres_ruta = datos.por_ruta
        self._estaciones = IndiceEstaciones(datos.estaciones)
        self._rutas = AlmacenRutas(TablaHash)
        for ruta, estacion in datos.rutas:
            self._rutas.agregar_al_final(ruta, estacion)
        self._horarios = IndiceHorarios(datos.horarios)
        self._historial = Historial()
        self._conteos = TablaHash()
        for nombre in datos.estaciones:
            self._conteos.guardar(nombre, 0)
        for _, nombre, _ in datos.horarios:
            self._conteos.guardar(nombre, self._conteos.obtener(nombre) + 1)

    def _estacion(self, nombre):
        return self._nombres.obtener(_normalizar(nombre))

    def _ruta(self, nombre):
        return self._nombres_ruta.obtener(_normalizar(nombre))

    def estado(self, nombre):
        return self._estaciones.estado(nombre)

    def autocompletar(self, prefijo, k):
        funcion = getattr(self._estaciones, "autocompletar", None)
        if funcion is None:
            raise ModuloPendiente("Falta integrar el índice de autocompletado R2.")
        return funcion(prefijo, k)

    def rango(self, desde, hasta):
        funcion = getattr(self._estaciones, "rango", None)
        if funcion is None:
            raise ModuloPendiente("Falta integrar el índice de rangos R3.")
        return funcion(desde, hasta)

    def conteos_vigentes(self):
        """Adaptador para R6. Incluye solo abiertas y eventos de rutas vigentes."""
        filas = []
        for nombre, cuenta in self._conteos.pares():
            if self.estado(nombre) == "ABIERTA":
                filas.append((nombre, cuenta))
        return filas

    def ranking(self, k):
        raise ModuloPendiente("Falta integrar el índice de ranking R6.")

    def proximo_bus(self, estacion, ruta, hora):
        hora_a_minutos(hora)
        nombre, linea = self._estacion(estacion), self._ruta(ruta)
        if nombre is None or linea is None or self.estado(nombre) != "ABIERTA":
            return None
        if not self._rutas.obtener(linea).contiene(nombre):
            return None
        return self._horarios.siguiente(nombre, linea, hora)

    def recorrido(self, ruta, al_reves=False):
        if not isinstance(al_reves, bool):
            raise TypeError("al_reves debe ser booleano")
        nombre = self._ruta(ruta)
        return [] if nombre is None else self._rutas.recorrido(nombre, al_reves)

    def viaje(self, origen, destino):
        inicio, fin = self._estacion(origen), self._estacion(destino)
        if inicio is None or fin is None:
            return None
        return planear_viaje(self._rutas, self._estaciones, inicio, fin)

    def _cambiar_estado(self, nombre, abierta):
        return self._estaciones.cambiar_estado(nombre, abierta)

    def _estado_publico(self, nombre, abierta):
        original = self._estacion(nombre)
        if original is None:
            return False
        anterior = self.estado(original) == "ABIERTA"
        if not self._cambiar_estado(original, abierta):
            return False
        self._historial.registrar(("estado", original, anterior, abierta))
        return True

    def cerrar(self, nombre):
        return self._estado_publico(nombre, False)

    def reabrir(self, nombre):
        return self._estado_publico(nombre, True)

    def _insertar(self, ruta, estacion, anterior):
        if anterior is None:
            cambio = self._rutas.insertar_al_inicio(ruta, estacion)
        else:
            cambio = self._rutas.agregar_parada(ruta, estacion, anterior)
        if cambio:
            cantidad = self._horarios.cantidad(estacion, ruta)
            self._conteos.guardar(estacion, self._conteos.obtener(estacion) + cantidad)
        return cambio

    def _quitar(self, ruta, estacion):
        if not self._rutas.quitar_parada(ruta, estacion):
            return False
        cantidad = self._horarios.cantidad(estacion, ruta)
        self._conteos.guardar(estacion, self._conteos.obtener(estacion) - cantidad)
        return True

    def agregar_parada(self, ruta, nueva, despues_de):
        linea = self._ruta(ruta)
        nombre, anterior = self._estacion(nueva), self._estacion(despues_de)
        if linea is None or nombre is None or anterior is None:
            return False
        if not self._insertar(linea, nombre, anterior):
            return False
        self._historial.registrar(("agregar", linea, nombre, anterior))
        return True

    def quitar_parada(self, ruta, estacion):
        linea, nombre = self._ruta(ruta), self._estacion(estacion)
        if linea is None or nombre is None:
            return False
        objeto = self._rutas.obtener(linea)
        if not objeto.contiene(nombre):
            return False
        anterior = objeto.anterior_de(nombre)
        self._quitar(linea, nombre)
        self._historial.registrar(("quitar", linea, nombre, anterior))
        return True

    def _aplicar(self, accion, inversa):
        tipo, primero, segundo, tercero = accion
        if tipo == "estado":
            self._cambiar_estado(primero, segundo if inversa else tercero)
        elif (tipo == "agregar" and inversa) or (tipo == "quitar" and not inversa):
            self._quitar(primero, segundo)
        else:
            self._insertar(primero, segundo, tercero)

    def deshacer(self):
        accion = self._historial.deshacer()
        if accion is None:
            return False
        self._aplicar(accion, True)
        return True

    def rehacer(self):
        accion = self._historial.rehacer()
        if accion is None:
            return False
        self._aplicar(accion, False)
        return True
