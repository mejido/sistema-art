from flask import Blueprint, render_template, session, redirect, url_for, current_app as app, make_response
import sqlite3
from collections import Counter
from fpdf import FPDF

cliente_bp = Blueprint('cliente', __name__)

@cliente_bp.route('/')
def cliente_dashboard():
    if 'usuario' not in session or session.get('rol') != 'cliente':
        return redirect(url_for('auth.index'))
    nombre_usuario = session.get('usuario')
    return render_template('cliente.html', nombre=nombre_usuario)

@cliente_bp.route('/tabla')
def ver_tabla():
    if 'usuario_id' not in session or session.get('rol') != 'cliente':
        return redirect(url_for('auth.index'))

    usuario_id = session['usuario_id']
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM datos_csv WHERE usuario_id = ?", (usuario_id,))
    datos = cur.fetchall()
    conn.close()

    return render_template('tabla_datos.html', datos=datos)

@cliente_bp.route('/grafico')
def ver_grafico():
    if 'usuario_id' not in session or session.get('rol') != 'cliente':
        return redirect(url_for('auth.index'))

    usuario_id = session['usuario_id']
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT cargo FROM datos_csv WHERE usuario_id = ?", (usuario_id,))
    datos = cur.fetchall()
    conn.close()

    cargos = [fila['cargo'] for fila in datos]
    conteo = Counter(cargos)

    labels = list(conteo.keys())
    valores = list(conteo.values())

    return render_template("grafico_datos.html", labels=labels, valores=valores)

@cliente_bp.route('/descargar')
def descargar_pdf():
    if 'usuario_id' not in session or session.get('rol') != 'cliente':
        return redirect(url_for('auth.index'))

    usuario_id = session['usuario_id']
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT nombre, empresa, cargo, ciudad FROM datos_csv WHERE usuario_id = ?", (usuario_id,))
    datos = cur.fetchall()
    conn.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Tabla de Datos ART", ln=True, align="C")
    pdf.ln(10)

    headers = ["Nombre", "Empresa", "Cargo", "Ciudad"]
    for h in headers:
        pdf.cell(48, 10, h, 1, 0, 'C')
    pdf.ln()

    for fila in datos:
        for campo in fila:
            pdf.cell(48, 10, str(campo), 1, 0, 'C')
        pdf.ln()

    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=datos_art_cliente.pdf'
    return response
