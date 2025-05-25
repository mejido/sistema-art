# Archivo generado o modificado el 22/05/2025 (hora local Argentina)

from flask import Blueprint, render_template, request, redirect, url_for, session, g, current_app as app
import sqlite3

usuarios = Blueprint('usuarios', __name__)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@usuarios.teardown_app_request
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@usuarios.route('/usuarios')
def listar_usuarios():
    if session.get('rol') != 'admin':
        return redirect(url_for('auth.index'))

    db = get_db()
    filtro = request.args.get('rol')
    if filtro in ['admin', 'cliente']:
        resultado = db.execute("SELECT * FROM usuarios WHERE rol = ? ORDER BY id DESC", (filtro,))
        titulo = "Administradores" if filtro == "admin" else "Clientes"
    else:
        resultado = db.execute("SELECT * FROM usuarios ORDER BY id DESC")
        titulo = "Todos"

    return render_template('usuarios.html', usuarios=resultado.fetchall(), titulo=titulo)

@usuarios.route('/usuario/nuevo', methods=['GET', 'POST'])
def nuevo_usuario():
    if session.get('rol') != 'admin':
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        usuario = request.form['usuario']
        rol = request.form['rol']
        clave = request.form['clave']
        db = get_db()
        db.execute("INSERT INTO usuarios (nombre, usuario, rol, clave) VALUES (?, ?, ?, ?)", (nombre, usuario, rol, clave))
        db.commit()
        return redirect(url_for('usuarios.listar_usuarios'))

    return render_template('usuario_form.html', user=None)

@usuarios.route('/usuario/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if session.get('rol') != 'admin':
        return redirect(url_for('auth.index'))

    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE id = ?", (id,)).fetchone()
    if not user:
        return redirect(url_for('usuarios.listar_usuarios'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        usuario_nombre = request.form['usuario']
        rol = request.form['rol']
        clave_actual = user['clave']

        if 'actualizar_contrasena' in request.form:
            nueva = request.form.get('nueva_contrasena', '')
            repetir = request.form.get('repetir_contrasena', '')
            if nueva != repetir:
                return render_template('editar_usuario.html', user=user, error='Las contraseñas no coinciden')
            clave = nueva
        else:
            clave = clave_actual

        db.execute("UPDATE usuarios SET nombre = ?, usuario = ?, rol = ?, clave = ? WHERE id = ?",
                   (nombre, usuario_nombre, rol, clave, id))
        db.commit()
        return redirect(url_for('usuarios.listar_usuarios'))

    return render_template('editar_usuario.html', user=user)

@usuarios.route('/usuario/eliminar/<int:id>')
def eliminar_usuario(id):
    if session.get('rol') != 'admin':
        return redirect(url_for('auth.index'))

    db = get_db()
    db.execute("DELETE FROM usuarios WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for('usuarios.listar_usuarios'))

@usuarios.route('/datos_art/<int:usuario_id>')
def datos_art(usuario_id):
    if session.get('rol') != 'admin':
        return redirect(url_for('auth.index'))

    db = get_db()
    datos = db.execute('SELECT nombre, empresa, cargo, ciudad FROM datos_csv WHERE usuario_id = ?', (usuario_id,)).fetchall()
    cliente = db.execute('SELECT nombre FROM usuarios WHERE id = ?', (usuario_id,)).fetchone()

    # Agrupar por ciudad
    ciudades = {}
    for fila in datos:
        ciudad = fila['ciudad']
        ciudades[ciudad] = ciudades.get(ciudad, 0) + 1

    labels = list(ciudades.keys())
    valores = list(ciudades.values())

    return render_template(
        'datos_cliente_admin.html',
        datos=datos,
        cliente_nombre=cliente['nombre'],
        usuario_id=usuario_id,
        labels=labels,
        valores=valores
    )


@usuarios.route('/descargar_pdf/<int:usuario_id>')
def descargar_pdf(usuario_id):
    from fpdf import FPDF
    import tempfile
    from flask import send_file

    db = get_db()
    datos = db.execute('SELECT nombre, empresa, cargo, ciudad FROM datos_csv WHERE usuario_id = ?', (usuario_id,)).fetchall()
    cliente = db.execute('SELECT nombre FROM usuarios WHERE id = ?', (usuario_id,)).fetchone()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, f"Reporte de Datos ART - {cliente['nombre']}", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 10, "Nombre", 1)
    pdf.cell(50, 10, "Empresa", 1)
    pdf.cell(50, 10, "Cargo", 1)
    pdf.cell(50, 10, "Ciudad", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 10)
    for fila in datos:
        pdf.cell(40, 10, str(fila['nombre']), 1)
        pdf.cell(50, 10, str(fila['empresa']), 1)
        pdf.cell(50, 10, str(fila['cargo']), 1)
        pdf.cell(50, 10, str(fila['ciudad']), 1)
        pdf.ln()

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp.name)

    return send_file(temp.name, as_attachment=True, download_name=f"datos_{cliente['nombre']}.pdf")
