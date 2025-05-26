from rutas.cliente_routes import cliente_bp
# Archivo generado o modificado el 22/05/2025 (hora local Argentina)

from flask import Flask
from rutas.auth import auth
from rutas.usuarios import usuarios
from rutas.csv import csv_rutas
from rutas.cliente import cliente_bp


app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = app.config['SECRET_KEY']

app.register_blueprint(auth)
app.register_blueprint(usuarios)
app.register_blueprint(csv_rutas)
app.register_blueprint(cliente_bp, url_prefix='/cliente')

if __name__ == '__main__':
    print("✅ Flask va a arrancar")
    app.run(debug=app.config['DEBUG'])


app.register_blueprint(cliente_bp)
