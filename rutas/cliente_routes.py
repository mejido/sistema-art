# cliente_routes.py
# Fecha: 26/05/2025 - 08:45 (ARG)

from flask import Blueprint, render_template, session, redirect, send_file

cliente_bp = Blueprint('cliente', __name__, url_prefix='/cliente')

@cliente_bp.route('/')
def dashboard():
    if 'usuario_id' not in session or session.get('rol') != 'cliente':
        return redirect('/')
    nombre = session.get('nombre', 'Cliente')
    return render_template('cliente.html', nombre=nombre)

@cliente_bp.route('/ver_tabla')
def ver_tabla():
    # Reemplazá con tu lógica real
    return render_template('tabla.html')

@cliente_bp.route('/ver_grafico')
def ver_grafico():
    # Reemplazá con tu lógica real
    return render_template('grafico.html')

@cliente_bp.route('/descargar_pdf')
def descargar_pdf():
    # Reemplazá con tu lógica real
    return send_file('ruta/al/archivo.pdf', as_attachment=True)
