import os
import csv
import sqlite3
from flask import Blueprint, request, redirect, url_for, render_template, flash, current_app as app

csv_rutas = Blueprint('csv_rutas', __name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@csv_rutas.route('/cargar_csv', methods=['GET', 'POST'])
def cargar_csv():
    db_path = app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Obtener lista de clientes
    cur.execute("SELECT id, usuario FROM usuarios WHERE rol = 'cliente'")
    clientes = cur.fetchall()

    if request.method == 'POST':
        usuario_id = request.form.get('usuario_id')
        archivo = request.files.get('archivo')

        if not usuario_id or not archivo:
            flash("❌ Debés seleccionar un cliente y un archivo.")
            return redirect(request.url)

        if archivo and allowed_file(archivo.filename):
            try:
                stream = archivo.stream.read().decode("utf-8").splitlines()
                reader = csv.DictReader(stream)

                campos_requeridos = {'usuario_id', 'nombre', 'empresa', 'cargo', 'ciudad'}
                if not campos_requeridos.issubset(reader.fieldnames):
                    flash("❌ El archivo CSV no tiene el formato correcto.")
                    return redirect(request.url)

                datos = list(reader)
                usuario_id_int = int(usuario_id)

                # Borrar datos actuales
                cur.execute("DELETE FROM datos_csv WHERE usuario_id = ?", (usuario_id_int,))

                # Insertar nuevos datos
                for fila in datos:
                    cur.execute(
                        "INSERT INTO datos_csv (usuario_id, nombre, empresa, cargo, ciudad) VALUES (?, ?, ?, ?, ?)",
                        (usuario_id_int, fila['nombre'], fila['empresa'], fila['cargo'], fila['ciudad'])
                    )
                conn.commit()

                # Guardar CSV
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)
                nombre_archivo = f"cliente_{usuario_id_int}.csv"
                archivo_path = os.path.join(UPLOAD_FOLDER, nombre_archivo)

                if os.path.exists(archivo_path):
                    os.remove(archivo_path)

                archivo.stream.seek(0)
                archivo.save(archivo_path)

                flash("✅ Carga exitosa para usuario_id " + str(usuario_id))
                return redirect(request.url)

            except Exception as e:
                flash("❌ Error procesando CSV: " + str(e))
                return redirect(request.url)
        else:
            flash("❌ Archivo no permitido. Solo se aceptan .csv.")

    conn.close()
    return render_template("cargar_csv.html", clientes=clientes)
