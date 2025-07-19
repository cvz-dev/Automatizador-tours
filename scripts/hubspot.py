import os
import requests
import csv
from dotenv import load_dotenv

# Cargar el token desde .env
load_dotenv()
hubspot_token = os.getenv('HUBSPOT_TOKEN')

# ID del formulario que quieres consultar
form_id = '924d72ee-3bb4-4f76-a9c7-4a129518fa91'

# Endpoint para obtener envíos del formulario
url = f'https://api.hubapi.com/form-integrations/v1/submissions/forms/{form_id}'

# Cabeceras para autenticar la solicitud
headers = {
    'Authorization': f'Bearer {hubspot_token}',
    'Content-Type': 'application/json'
}

# Hacer la solicitud
response = requests.get(url, headers=headers)

# Revisar el resultado
if response.status_code == 200:
    data = response.json()
    submissions = data.get('results', [])

    ruta_archivo = r'..\data\regisros_formulario.csv'

    # Guardar en CSV
    with open(ruta_archivo, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['submittedAt', 'values']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for submission in submissions:
            writer.writerow({
                'submittedAt': submission.get('submittedAt'),
                'values': submission.get('values')
            })

    print(f"Registros guardados en 'form_submissions.csv'")
else:
    print(f"Error {response.status_code}: {response.text}")