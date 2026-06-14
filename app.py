from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import os
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_apuntes_forge'

CARPETA_SUBIDAS = os.path.join('static', 'apuntes_pdf')

app.config['UPLOAD_FOLDER'] = CARPETA_SUBIDAS
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

if not os.path.exists(CARPETA_SUBIDAS):
    os.makedirs(CARPETA_SUBIDAS)
Ruta principal inicial:
@app.route('/')
def inicio():
    return render_template('inicio.html')
Servidor:
if __name__ == '__main__':
    app.run(debug=True)



def conectar_bd():
    conexion = sqlite3.connect('apuntes.db')
    conexion.row_factory = sqlite3.Row
    return conexion

def inicializar_bd():
    conexion = conectar_bd()
    cursor = conexion.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS apuntes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            materia TEXT NOT NULL,
            categoria TEXT NOT NULL,
            autor TEXT NOT NULL,
            archivo_nombre TEXT NOT NULL,
            estrellas INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM apuntes')
    if cursor.fetchone()[0] == 0:
        datos_semilla = [
            ("Resumen Primer Parcial - Cálculo Integral", "Cálculo II", "Ciencias Básicas", "Carlos Mendoza", "ejemplo_calculo.pdf", 12),
            ("Guía Completa de Programación Orientada a Objetos", "Programación I", "Ingeniería", "Laura Restrepo", "ejemplo_poo.pdf", 24)
        ]
        cursor.executemany('''
            INSERT INTO apuntes (titulo, materia, categoria, autor, archivo_nombre, estrellas)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', datos_semilla)
        conexion.commit()
    
    conexion.close()





@app.route('/subir', methods=['GET', 'POST'])
def subir_apunte():
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        materia = request.form.get('materia', '').strip()
        categoria = request.form.get('categoria', '').strip()
        autor = request.form.get('autor', '').strip()
        archivo = request.files.get('archivo')
        
        if not (titulo and materia and categoria and autor and archivo):
            flash('Todos los campos son obligatorios.', 'error')
            return redirect(url_for('subir_apunte'))
        
        if archivo.filename == '':
            flash('Archivo no válido.', 'error')
            return redirect(url_for('subir_apunte'))
        
        nombre_seguro = secure_filename(archivo.filename)
        ruta_guardado = os.path.join(app.config['UPLOAD_FOLDER'], nombre_seguro)
        archivo.save(ruta_guardado)
        
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute('''
            INSERT INTO apuntes (titulo, materia, categoria, autor, archivo_nombre)
            VALUES (?, ?, ?, ?, ?)
        ''', (titulo, materia, categoria, autor, nombre_seguro))
        conexion.commit()
        conexion.close()
        
        flash('¡Material compartido con éxito!', 'exito')
        return redirect(url_for('inicio'))
    
    return render_template('subir_apunte.html')
Archivo: templates/subir_apunte.html

html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subir Apunte --- ApuntesForge</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/estilos.css') }}">
</head>
<body>
    <nav class="navbar">
        <div class="nav-contenedor">
            <a href="/" class="logo" style="font-size: 0.85rem; color: var(--texto-gris);">← Volver al catálogo</a>
        </div>
    </nav>
    <main class="contenedor" style="margin: auto;">
        <div class="tarjeta-formulario">
            <div style="text-align: center; margin-bottom: 2rem;">
                <h2 style="font-size: 1.4rem; font-weight: 800; margin: 0;">Compartir conocimiento</h2>
                <p style="font-size: 0.75rem; color: var(--texto-gris); margin-top: 0.25rem;">Tu documento se ordenará automáticamente según las reacciones de la facultad.</p>
            </div>
            <form method="POST" action="/subir" enctype="multipart/form-data">
                <div class="form-grupo">
                    <label>Título del Apunte</label>
                    <input type="text" name="titulo" required maxlength="100" placeholder="Ej: Apuntes Primer Corte Física II" class="form-input">
                </div>
                <div class="form-grupo">
                    <label>Materia o Asignatura</label>
                    <input type="text" name="materia" required maxlength="50" placeholder="Ej: Física II" class="form-input">
                </div>
                <div class="form-grupo">
                    <label>Categoría General</label>
                    <select name="categoria" required class="form-input" style="cursor: pointer; height: 38px;">
                        <option value="" disabled selected>Selecciona una área...</option>
                        <option value="Ciencias Básicas">Ciencias Básicas</option>
                        <option value="Ingeniería">Ingeniería</option>
                        <option value="Humanidades">Humanidades</option>
                    </select>
                </div>
                <div class="form-grupo">
                    <label>Nombre del Autor</label>
                    <input type="text" name="autor" required maxlength="60" placeholder="Ej: Carlos Mendoza" class="form-input">
                </div>
                <div class="form-grupo" style="margin-top: 1.5rem;">
                    <div class="dropzone">
                        <label style="margin-bottom: 0.5rem; display: block; cursor: pointer;">Seleccionar archivo Universitario (.PDF)</label>
                        <input type="file" name="archivo" accept=".pdf" required style="font-size: 0.75rem; color: var(--texto-gris); cursor: pointer;">
                    </div>
                </div>
                <button type="submit" class="btn-principal" style="width: 100%; padding: 0.85rem; margin-top: 1rem;">
                    🚀 Publicar Documento Gratis
                </button>
            </form>
        </div>
    </main>
</body>
</html>
