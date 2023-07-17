import os
from io import BytesIO
import pdfplumber
import re
#import pandas as pd
#from flask import Flask, render_template, request, send_file, make_response, flash, redirect, url_for
from flask import Flask, render_template, request, make_response, flash, redirect, url_for

#from flask_sqlalchemy import SQLAlchemy, session
from flask_sqlalchemy import SQLAlchemy
# Modulo para crear un archivo excel tipo xlsx
import xlsxwriter
from werkzeug.utils import secure_filename

from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_wtf.csrf import CSRFProtect


# Creación de la aplicación con Flask
app = Flask(__name__)

# Conectamos a la base de datos admin_base
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resoluciones.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app.secret_key = 'l=#*)16l(c8@=qbzqthryo&0tiih&fvhg63_hjz8u()k$-3k&q'   # Agregado por Leoncio
app.config['SECRET_KEY'] = 'l=#*)16l(c8@=qbzqthryo&0tiih&fvhg63_hjz8u()k$-3k&q'   # Agregado por Leoncio

# Vinculamos SQLAlchemy a la aplicación
db = SQLAlchemy(app)


#-- Manejador de Autenticación.
login_manager = LoginManager(app)

#-- Para proteger login con token csfr
csrf = CSRFProtect(app)

# Configuración para subir archivos PDF
app.config['UPLOAD_FOLDER'] = 'resoluciones'  # Ruta de la carpeta de destino en el servidor
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'PDF'}  # Extensiones de archivo permitidas

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Modelo de datos de Usuario
class Usuario(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	usuario = db.Column(db.String(15))
	password = db.Column(db.String(40))
	email = db.Column(db.String(80))
	telefono = db.Column(db.String(20))
	estatus = db.Column(db.Boolean)

class Resolucion(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	fresolucion = db.Column(db.String(30))
	nresolucion = db.Column(db.String(10))
	nombre = db.Column(db.String(60))
	infraccion = db.Column(db.String(5))
	valor = db.Column(db.Float)
	acta = db.Column(db.String(30))
	fechaActa = db.Column(db.String(30))
	placa = db.Column(db.String(10))
	servicio = db.Column(db.String(50))
	

# Creacion de la base de datos en SQLite 3 
# Creación de la tablas en base a los modelos
# Deshabilitarlo luego de ejecutarlo
#with app.app_context():     
#    db.create_all()
##########################

# Creación de rutas

# Ruta principal - Inicio de la Aplicación
@app.route('/', methods=['GET', 'POST'])
def home():
	#return "Hola Programadores"
	return render_template('home.html')


#=====================================================================================================

@login_manager.user_loader
def load_user(id):
	return Usuario.query.filter_by(id=id).first()

def status_401(error):
	return redirect(url_for('login'))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

def status_404(error):
	return "<h2>Página no encontrada</h2>", 404

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		
		usuario = Usuario.query.filter_by(usuario=username).first()
		if usuario:
			if usuario.password == password:
				login_user(usuario)
				return render_template('home.html', usuario=usuario)
				
			else:
				flash("Password inválido...")
				return render_template('login.html')
			
		else:
			flash("Usuario no registrado...")
			return render_template('login.html')
	else:
		return render_template('login.html')

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('login'))

#-- CRUD Usuarios
@app.route('/usuarios', methods=['GET', 'POST'])
@login_required
def usuarios():
	if current_user.usuario == "admin":
		usuarios = Usuario.query.all()
		return render_template('usuario-listar.html', usuarios=usuarios)
	else:
		return render_template('usuario-aviso.html')

@app.route('/usuarios/nuevo', methods=['GET', 'POST'])
def usuario_nuevo():
	accion = "Nuevo"
	usuario = Usuario()
	if request.method == 'POST':
		usuario.usuario = request.form.get('usuario')
		usuario.password = request.form.get('password')
		usuario.email = request.form.get('email')
		usuario.telefono = request.form.get('telefono')
		usuario.estatus = bool(request.form.get('estatus'))
		password2 = request.form.get('confirmar_password')
		
		if usuario.usuario!= "" and usuario.password!= "" and usuario.email!= "" and usuario.telefono!= "" :
			if usuario.password == password2:
				db.session.add(usuario)
				db.session.commit()
			else:
				flash("Password no coinciden...")
				return render_template('usuario-form.html', accion=accion, usuario=usuario)
		else:
			flash("Debe indicar todos los campos...")
			return render_template('usuario-form.html', accion=accion, usuario=usuario)
		return redirect(url_for('usuarios'))
	return render_template('usuario-form.html', accion=accion, usuario=usuario)

@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def usuarios_editar(id):
	accion = "Editar"
	usuario = Usuario.query.filter_by(id=id).first()
	
	if request.method == 'POST':
		usuario.usuario = request.form.get('usuario')
		usuario.password = request.form.get('password')
		usuario.email = request.form.get('email')
		usuario.telefono = request.form.get('telefono')
		usuario.estatus = bool(request.form.get('estatus'))
		password2 = request.form.get('confirmar_password')
		
		if usuario.usuario!= "" and usuario.password!= "" and usuario.email!= "" and usuario.telefono!= "" :
			if usuario.password == password2:
				db.session.add(usuario)
				db.session.commit()
			else:
				flash("Password no coinciden...")
				return render_template('usuario-form.html', accion=accion, usuario=usuario)
		else:
			flash("Debe indicar todos los campos...")
			return render_template('usuario-form.html', accion=accion, usuario=usuario)
		return redirect(url_for('usuarios'))
	
	return render_template('usuario-form.html', accion=accion, usuario=usuario)


@app.route('/usuarios/eliminar/<int:id>', methods=['GET', 'POST'])
def usuarios_eliminar(id):
	usuario = Usuario.query.filter_by(id=id).first()
	if request.method == 'POST':
		db.session.delete(usuario)
		db.session.commit()
		return redirect(url_for('usuarios'))
	return render_template('usuario-eliminar.html', usuario=usuario)

#==============================================================================	=======================

# Carga de las resoluciones
@app.route('/cargaresol', methods=['GET', 'POST'])
def cargaresol():
    # Obtener el valor de la UIT ingresado por el usuario
	uit = 4950

	# Obtener la lista de archivos PDF en el directorio
	#PATH = "resoluciones"
	PATH = "/home/resoluciones/Resoluciones-main/resoluciones"
	files = []

	for dirpath, dirnames, filenames in os.walk(PATH):
		for filename in filenames:
			if filename.endswith('.pdf'):
				files.append(os.path.join(dirpath, filename))

	fresolucion = []
	nresolucion = []
	nombre = []
	infraccion = []
	valor = []
	acta = []
	fechaActa = []
	placa = []
	servicio = []

	for filename in files:
		f_resolucion = ""
		n_resolucion = ""
		nombre_rs = ""
		t_infraccion = ""
		valor_m = ""
		c_acta = ""
		fecha_Acta = ""
		n_placa = ""
		t_servicio = ""

		with pdfplumber.open(filename) as pdf:
			for page in pdf.pages:
				text = page.extract_text()
				lines = text.split('\n')

				for line in lines:
					if 'Trujillo, ' in line:
						f_resolucion = line.split('Trujillo, ')[1].strip()

				# Obtener el nombre del archivo sin la extensión .pdf
				nombre_archivo = os.path.splitext(os.path.basename(filename))[0]

				# Utilizar expresión regular para extraer el número de resolución y el nombre o razón social del archivo
				matches_nombre = re.search(r"(?:R\.G\.R\.-)?(\d+-\d+)-(.+)", nombre_archivo)
				if matches_nombre:
					n_resolucion = matches_nombre.group(1)
					nombre_rs = matches_nombre.group(2).strip().split(',')[0]

				# Eliminar la parte " - copia (5)" del nombre
				nombre_rs = re.sub(r'\s*-\s*copia\s*\(\d+\)\s*', '', nombre_rs)

				for line in lines:
					if 'tipificada con Código ' in line:
						matches_infraccion = re.search(r'tipificada con Código ([A-Za-z]\.[0-9])', line)
						if matches_infraccion:
							t_infraccion = matches_infraccion.group(1)
						else:
							t_infraccion = ""

					if 'equivalente a' in line and 'de la UIT' in line:
						matches_valor = re.search(r"equivalente a ([\d.]+(?:\.\d+)?) de la UIT", line)
						valor_m = str(round(float(matches_valor.group(1)) * uit)) if matches_valor else ""

					if 'El Acta de Control ' in line:
						c_acta = line.split('El Acta de Control ')[1].split(',')[0].replace('N°', '')

					if 'de fecha ' in line:
						fecha_match = re.search(r'\d+ de \w+ de \d+', line)
						if fecha_match:
							fecha_Acta = fecha_match.group(0)
						else:
							fecha_Acta = ""

					matches_placa = re.search(r"(placa de rodaje|unidad vehicular) ([A-Z0-9-]+)", line)
					if matches_placa:
						n_placa = matches_placa.group(2).replace(',', '')

					if 'servicio: ' in line:
						t_servicio = line.split('Modalidad de servicio: ')[1].strip()

		fresolucion.append(f_resolucion)
		nresolucion.append(n_resolucion)
		nombre.append(nombre_rs)
		infraccion.append(t_infraccion)
		valor.append(valor_m)
		acta.append(c_acta)
		fechaActa.append(fecha_Acta)
		placa.append(n_placa)
		servicio.append(t_servicio)

	data = {
		'Fecha de resolución': fresolucion,
		'N°': nresolucion,
		'Nombre o razón social': nombre,
		'Infracción': infraccion,
		'Valor': valor,
		'Acta': acta,
		'Fecha de acta': fechaActa,
		'Placa': placa,
		'Modalidad de servicio': servicio
	}

	# Crear Filas de datos y cargarlos en la tabla/modelo Resolucion
	lista_act = []
	
	for i in range(len(fresolucion)):
		# Creación de las filas
		fila = [fresolucion[i], nresolucion[i], nombre[i], infraccion[i], valor[i], acta[i], fechaActa[i], placa[i], servicio[i]]
		lista_act.append(fila)
		
		# Carga de datos en la tabla/modelo Resolucion
		resolucion = Resolucion()
		
		resolucion.fresolucion = fresolucion[i]
		resolucion.nresolucion = nresolucion[i]
		resolucion.nombre = nombre[i]
		resolucion.infraccion = infraccion[i]
		resolucion.valor = valor[i]
		resolucion.acta = acta[i]
		resolucion.fechaActa = fechaActa[i]
		resolucion.placa = placa[i]
		resolucion.servicio = servicio[i]
  
		db.session.add(resolucion)
		db.session.commit()
  
    # Renderizar el template cargaresol.html con el contexto de datos: files, datos
	files_new = [item.replace("resoluciones\\", "") for item in files]
	return render_template('cargaresol.html', files = files_new, datos=lista_act)

# Formulario para subir PDF
@app.route('/subir_pdf', methods=['GET'])
def subir_pdf():
	return render_template('subir_pdf.html')

# Formulario para subir PDF a la carpeta resoluciones en el servidor
@app.route('/cargar_pdf', methods=['POST'])
def cargar_pdf():
	if 'archivo' not in request.files:
		return 'No se seleccionó ningún archivo'

	archivo = request.files['archivo']

	if archivo.filename == '':
		mensaje = 'No se seleccionó ningún archivo'
		return render_template('result_pdf.html', mensaje=mensaje)

	if archivo and allowed_file(archivo.filename):
		filename = secure_filename(archivo.filename)
		archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		mensaje = 'Archivo cargado con éxito'
		return render_template('result_pdf.html', mensaje=mensaje)
	else:
		mensaje = 'Extensión de archivo no permitida'
		return render_template('result_pdf.html', mensaje=mensaje)

# Descarga de la tabla de resoluciones
@app.route('/descargar_excel', methods=['GET'])
def descargar_excel():
    # Se traen todos los resgistros
    # Pero se pueden aplicar filtros personalizados
    resoluciones = Resolucion.query.all()

    # Crear el archivo Excel
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    # Escribir los encabezados de la tabla
    worksheet.write(0, 0, 'ID')
    worksheet.write(0, 1, 'Fecha Resolución')
    worksheet.write(0, 2, 'N° Resolución')
    worksheet.write(0, 3, 'Nombre')
    worksheet.write(0, 4, 'Infracción')
    worksheet.write(0, 5, 'Valor')
    worksheet.write(0, 6, 'Acta')
    worksheet.write(0, 7, 'Fecha Acta')
    worksheet.write(0, 8, 'Placa')
    worksheet.write(0, 9, 'Servicio')

    # Escribir los datos de las resoluciones
    for i, resolucion in enumerate(resoluciones):
        worksheet.write(i+1, 0, resolucion.id)
        worksheet.write(i+1, 1, resolucion.fresolucion)
        worksheet.write(i+1, 2, resolucion.nresolucion)
        worksheet.write(i+1, 3, resolucion.nombre)
        worksheet.write(i+1, 4, resolucion.infraccion)
        worksheet.write(i+1, 5, resolucion.valor)
        worksheet.write(i+1, 6, resolucion.acta)
        worksheet.write(i+1, 7, resolucion.fechaActa)
        worksheet.write(i+1, 8, resolucion.placa)
        worksheet.write(i+1, 9, resolucion.servicio)

    workbook.close()

    # Preparar la respuesta para descargar el archivo Excel
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=resoluciones.xlsx'
    response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    return response

if __name__ == '__main__':
	app.register_error_handler(401, status_401)
	app.register_error_handler(404, status_404)
	csrf.init_app(app)
	app.run(debug=False)
