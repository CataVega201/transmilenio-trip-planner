"""Servidor web del proyecto. La logica de la red vivira en motor/."""

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/api/estado")
def estado_servidor():
    return jsonify(estado="ok", mensaje="Servidor de TransMilenio funcionando")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
