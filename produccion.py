"""Servidor público: React y Flask comparten dominio y una instancia de Red."""
import os
from pathlib import Path
from threading import Lock

from waitress import serve
from werkzeug.exceptions import TooManyRequests

from rendimiento.medir import medir_api
from servidor import crear_app

RAIZ = Path(__file__).resolve().parent
_medicion = Lock()


def medir_publico(tamanos, repeticiones):
    # Una sola medición a la vez evita multiplicar el consumo de RAM del servidor.
    if not _medicion.acquire(blocking=False):
        raise TooManyRequests("Ya hay una medición en curso. Intenta de nuevo cuando termine.")
    try:
        return medir_api(tamanos, repeticiones)
    finally:
        _medicion.release()


app = crear_app(RAIZ / "datos", RAIZ / "frontend" / "dist", medir=medir_publico)


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", "10000")),
          threads=4, channel_timeout=1800)
