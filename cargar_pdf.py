import os
import pdfplumber
import re
import pandas as pd

# Obtener el valor de la UIT ingresado por el usuario
uit = 4950

# Obtener la lista de archivos PDF en el directorio
PATH = "resoluciones"
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

#print(data)
#df = pd.DataFrame(data)
#df
for i in range(len(fresolucion)):
  print(fresolucion[i], nresolucion[i], nombre[i], infraccion[i], valor[i], acta[i], fechaActa[i], placa[i], servicio[i])
