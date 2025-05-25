from flask import Blueprint, render_template, request, redirect, session, url_for, g, current_app as app, flash
import sqlite3

auth = Blueprint('auth', __name__)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@auth.teardown_app_request
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@auth.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['password']
        db = get_db()
        cur = db.execute("SELECT * FROM usuarios WHERE usuario = ? AND clave = ?", (usuario, clave))
        user = cur.fetchone()
        if user:
            session['usuario'] = user['usuario']
            session['usuario_id'] = user['id']
            session['rol'] = user['rol']
            if user['rol'] == 'admin':
                return redirect(url_for('auth.admin'))
            else:
                return redirect(url_for('cliente.cliente_dashboard'))
        else:
            flash('Usuario o clave incorrectos')
    return render_template('index.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index'))

@auth.route('/admin')
def admin():
    if session.get('rol') != 'admin':
        return redirect(url_for('auth.index'))
    return render_template('admin.html')
