from flask import Flask
from rutas.usuarios import usuarios
from rutas.auth import auth
from rutas.csv import csv_rutas
from rutas.cliente import cliente_bp
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta'
app.config['DATABASE'] = 'netbroker.db'  # ← Esta línea soluciona el KeyError

# Registrar Blueprints
app.register_blueprint(auth)
app.register_blueprint(usuarios)
app.register_blueprint(csv_rutas)
app.register_blueprint(cliente_bp, url_prefix='/cliente')

# Ejecutar en producción
if __name__ == '__main__':
    port = 5001
    app.run(host='0.0.0.0', port=port)