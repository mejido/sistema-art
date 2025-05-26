
from flask import Flask
import sqlite3

app = Flask(__name__)

@app.route('/ver-clientes')
def ver_clientes():
    conn = sqlite3.connect('netbroker.db')
    cur = conn.cursor()
    cur.execute("SELECT usuario, clave, rol FROM usuarios")
    datos = cur.fetchall()
    conn.close()
    return '<br>'.join([f"{u} | {c} | {r}" for u, c, r in datos])
