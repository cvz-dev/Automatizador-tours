import os
import requests
import csv
from dotenv import load_dotenv

import pandas as pd
from datetime import datetime

def debug_labels_formulario(form_id, headers):
    """Debug: muestra todos los campos encontrados"""
    url_form = f'https://api.hubapi.com/marketing/v3/forms/{form_id}'
    
    response = requests.get(url_form, headers=headers)
    
    if response.status_code == 200:
        form_data = response.json()
        labels_dict = {}
        
        print("=== DEBUG: Campos encontrados ===")
        for i, group in enumerate(form_data.get('fieldGroups', [])):
            print(f"\nGrupo {i+1}:")
            for j, field in enumerate(group.get('fields', [])):
                name = field.get('name', 'SIN_NAME')
                label = field.get('label', 'SIN_LABEL')
                field_type = field.get('fieldType', 'SIN_TIPO')
                
                print(f"  Campo {j+1}: name='{name}' | label='{label}' | type='{field_type}'")
                
                # Buscar campos específicos problemáticos
                if 'visita' in name.lower():
                    print(f"    *** CAMPO DE VISITA ENCONTRADO: {name} -> {label}")
                
                if name and label:
                    labels_dict[name] = label
        
        print(f"\n=== Total labels procesados: {len(labels_dict)} ===")
        return labels_dict
    else:
        print(f"Error: {response.status_code}")
        return {}

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

labels_campos = debug_labels_formulario(form_id, headers)
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

    # Crear un diccionario con los datos de registro
    fila = {
        'fecha_envio': fecha_envio.strftime('%Y-%m-%d %H:%M%S'),
        'conversion_id': registro['conversionId']
    }

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