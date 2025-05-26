from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "clave-secreta"

def get_db_connection():
    conn = sqlite3.connect('netbroker.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND clave = ?", (usuario, clave))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            session['usuario_id'] = resultado['id']
            session['rol'] = resultado['rol']
            session['usuario'] = resultado['usuario']

            if resultado['rol'] == 'admin':
                return redirect('/admin')
            elif resultado['rol'] == 'cliente':
                return redirect('/cliente')
        else:
            error = 'Credenciales incorrectas'

    return render_template('index.html', error=error)

@app.route('/admin')
def admin():
    if 'usuario_id' not in session or session.get('rol') != 'admin':
        return redirect('/')
    return render_template('admin.html', usuario=session.get('usuario'))

@app.route('/cliente')
def cliente():
    if 'usuario_id' not in session or session.get('rol') != 'cliente':
        return redirect('/')
    return render_template('cliente.html', usuario=session.get('usuario'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
