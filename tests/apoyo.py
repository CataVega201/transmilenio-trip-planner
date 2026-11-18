"""Apoyo de pruebas de Alejandro. Vive fuera de motor/.

Mientras un modulo de otro autor no este integrado en motor/, las pruebas usan
un doble de tests/dobles/ con la interfaz acordada en docs/CONTRATOS.md. En
cuanto el archivo real existe en motor/, se usa el real y el doble se ignora.
Los dobles NO son entregables del motor ni reemplazan el trabajo de su autor.
"""

import importlib.util
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOBLES = os.path.join(RAIZ, "tests", "dobles")
MODULOS_AJENOS = ["tabla_hash", "estaciones", "ranking", "horarios", "fila"]

if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)


def preparar_motor():
    """Registra un doble por cada modulo ajeno ausente. Devuelve sus nombres."""
    usados = []
    for nombre in MODULOS_AJENOS:
        completo = "motor." + nombre
        if os.path.exists(os.path.join(RAIZ, "motor", nombre + ".py")):
            continue
        usados.append(nombre)
        if completo in sys.modules:
            continue
        ruta = os.path.join(DOBLES, nombre + ".py")
        if not os.path.exists(ruta):
            continue
        especificacion = importlib.util.spec_from_file_location(completo, ruta)
        modulo = importlib.util.module_from_spec(especificacion)
        sys.modules[completo] = modulo
        especificacion.loader.exec_module(modulo)
    return usados
