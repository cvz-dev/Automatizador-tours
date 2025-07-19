import os
import requests
import csv
from dotenv import load_dotenv

import pandas as pd
from datetime import datetime

# Función para obtener los labels de los campos del formulario
def obtener_labels_formulario(form_id, headers):
    url_form = f'https://api.hubapi.com/marketing/v3/forms/{form_id}'

    response = requests.get(url_form, headers=headers)

    # Se ejecuta solo si la consulta es exitosa
    if response.status_code == 200:
        form_data = response.json()
        labels_dict = {}
        
        # Buscar en fieldgroups
        for group in form_data.get('fieldGroups', []):
            for field in group.get('fields', []):
                name = field.get('name', [])
                label = field.get('label', [])
                if name and label:
                    labels_dict[name] = label
        
        # Dado a que hay campos condicionales entonces creamos un nuevo diccionario
        # con los labels faltantes
        labels_extras = {
            'dia_de_visita_norte': 'Día de visita Norte',
            'dia_de_visita_sur_pa': 'Día de visita Sur',
            'preparatoria_otra': 'Escribe tu Preparatoria aquí',
            'txt_autocomplete_schools': 'Autocompletado de escuelas',
        }

        # Agregamos los labels extra al conjunto de labels total
        labels_dict.update(labels_extras)

        return labels_dict
    else:
        print(f"Error obteniendo labels: {response.status_code}")
        return {}

# Función para reordenar las columnas del df
def reordenar_columnas(df, orden_correcto):
    # Obtener columnas actuales del df
    columnas_actuales = list(df.columns)
    
    # Ordenar con las columnas deseadas
    columnas_ordenadas = []
    for columna in orden_correcto:
        if columna in columnas_actuales:
            columnas_ordenadas.append(columna)

    # Agregamos las columnas que no estén consideradas
    # Por list comprenhension
    columnas_extras = [col for col in df.columns if col not in orden_correcto]
    # Forma clásica con un ciclo for
    """
    columnas_extras = []
    for col in df.columns:
        if col not in orden_deseado_set:
            columnas_restantes.extras(col)
    """

    # Juntamos ambos grupos de columnas para obtener el orden definitivo
    columnas_finales = columnas_ordenadas + columnas_extras
    df_reordenado = df[columnas_finales]

    return df_reordenado

orden_columnas = [
    'Nombre',
    'Apellido paterno',
    'Apellido materno',
    'Email',
    'Celular',
    'Estado de procedencia',
    'Preparatoria',
    'Escribe tu Preparatoria aquí'
    '¿Cúal es tu grado escolar?'
    'Lienciatura 1'
    'Periodo de intrés'
    'Campus de interés'
    'Día de visita Norte'
    'Día de visita Sur'
    'Nombre completo del acompañante'
    'Correo acompañante'
]

# Cargar el token desde .env
load_dotenv()
hubspot_token = os.getenv('HUBSPOT_TOKEN')

# ID del formulario que quieres consultar
form_id = '924d72ee-3bb4-4f76-a9c7-4a129518fa91'

# Endpoint para obtener envíos del formulario
url = f'https://api.hubapi.com/form-integrations/v1/submissions/forms/{form_id}'

# Headers para la autenticación
headers = {
    'Authorization': f'Bearer {hubspot_token}',
    'Content-Type': 'application/json'
}

# Arreglo para guardar todos los registros
registros = []

# Parámetros para la primera solicitud
params = {
    'limit': 50 # Número máximo de registros que se pueden solicitar por consulta
}

token_siguiente_pagina = None
contador_paginas = 0
objetivo_registros = 250

print("Iniciando descarga de registros...")

labels_campos = obtener_labels_formulario(form_id, headers)
print(f"Labels obtenidos: {len(labels_campos)}")

while len(registros) < objetivo_registros:

    # Si existe, agregar token para la siguiente página
    if token_siguiente_pagina:
        params['after'] = token_siguiente_pagina

    # Hacer la solicitud
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        contador_paginas += 1

        # Agregar los registros de esta página a al arreglo
        registros.extend(data['results'])

        print(f"Pagina {contador_paginas}: {len(data['results'])} registros | Total: {len(registros)}")

        # Verificar si hay más páginas
        if 'paging' in data and 'next' in data['paging']:
            # Obtener el token de la URL
            proxima_url = data['paging']['next']['link']
            token_siguiente_pagina = proxima_url.split('after=')[1].split('&')[0]
        else:
            print("No hay más páginas disponibles")
            break
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        break

print(f"\nDescarga completada Total de registros: {len(registros)}")

# Datos para el excel
print("Ahora va excel")

# Lista para almacenar los datos
datos_procesados = []

for registro in registros:
    # Convertir timestamp a fecha legible
    fecha_envio = datetime.fromtimestamp(registro['submittedAt'] / 1000)

    """
    # Crear un diccionario con los datos de registro
    fila = {
        'fecha_envio': fecha_envio.strftime('%Y-%m-%d %H:%M%S'),
        'conversion_id': registro['conversionId']
    }
    """
    fila = {}

    #Extraer todos los valores del formulario
    for campo in registro['values']:
        fila[campo['name']] = campo['value']

    datos_procesados.append(fila)

# Crear DataFrame y exportar a Excel
df = pd.DataFrame(datos_procesados)

# Renombrar columnas usando los labels obtenidos
if labels_campos:
    df.rename(columns=labels_campos, inplace=True)

# Nombre y path del excel
archivo_excel = f'../data/regitros_tours_con_API.xlsx'

# Exportar a Excel
df.to_excel(archivo_excel, index=False)

print(f"Excel creado exitosamente Archivo: {archivo_excel}")
print(f"Registros procesados: {len(datos_procesados)}")
print(f"Columnas en el Excel: {len(df.columns)}")