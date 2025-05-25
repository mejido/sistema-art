from flask import Flask
from rutas.usuarios import usuarios
from rutas.auth import auth
from rutas.csv import csv
from rutas.cliente import cliente_bp
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Registrar Blueprints
app.register_blueprint(auth)
app.register_blueprint(usuarios)
app.register_blueprint(csv)
app.register_blueprint(cliente_bp)

# Ejecutar en producción (Railway)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
