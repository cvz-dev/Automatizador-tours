from google.cloud import storage
from google.oauth2 import service_account
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Conectarse a Google Cloud Storage
def obtener_cliente():
    """Obtiene cliente de GCS compatible con GitHub Actions y desarrollo local"""
    load_dotenv()
    
    credenciales = os.getenv("CREDENCIAL_GOOGLE")
    
    if not credenciales:
        raise Exception("Variable de entorno CREDENCIAL_GOOGLE no encontrada")
    
    try:
        # Caso 1: GitHub Actions - la variable contiene el JSON completo
        if credenciales.strip().startswith('{'):
            credentials_dict = json.loads(credenciales)
            credentials = service_account.Credentials.from_service_account_info(credentials_dict)
            
        # Caso 2: Desarrollo local - Manejo de ruta inteligente
        else:
            # Si la ruta no es absoluta, la construimos relativa a este archivo (.py)
            if not os.path.isabs(credenciales):
                # Obtiene la carpeta donde está 'cloud_storage.py' (scripts/)
                base_path = os.path.dirname(os.path.abspath(__file__))
                # Une 'scripts/' con 'credenciales/tours-automaticos-clave.json'
                ruta_completa = os.path.join(base_path, credenciales)
            else:
                ruta_completa = credenciales

            if os.path.isfile(ruta_completa):
                credentials = service_account.Credentials.from_service_account_file(ruta_completa)
            else:
                raise Exception(f"No se encontró el archivo JSON en: {ruta_completa}")
        
        return storage.Client(credentials=credentials)
        
    except Exception as e:
        raise Exception(f"Error al cargar credenciales: {e}")

# Subir un archivo a Google Cloud Storage
def subir_archivo(ruta_local, ruta_nube, nombre_bucket="tours-automaticos"):
    #if not os.path.exists(ruta_local):
        #raise FileNotFoundError(f"Archivo no encontrado: {ruta_local}")
    
    try:
        cliente = obtener_cliente()
        bucket = cliente.bucket(nombre_bucket)
        archivo_gcs = bucket.blob(ruta_nube)
        
        with open(ruta_local, 'rb') as file:
            archivo_gcs.upload_from_file(file)
        
        return {
            'gcs_path': ruta_nube,
            'public_url': f"https://storage.googleapis.com/{nombre_bucket}/{ruta_nube}",
        }
        
    except Exception as e:
        raise Exception(f"Error al subir: {e}")


# Descarcar archivo de Google Cloud Storage
def descargar_archivo(ruta_local, ruta_nube, nombre_bucket="tours-automaticos"):
    try:
        cliente = obtener_cliente()
        bucket = cliente.bucket(nombre_bucket)
        archivo_gcs = bucket.blob(ruta_nube)
        
        """"
        if not archivo_gcs.exists():
            raise FileNotFoundError(f"Archivo no existe en GCS: {ruta_nube}")
        """
        
        with open(ruta_local, 'wb') as file:
            archivo_gcs.download_to_file(file)
        
    except Exception as e:
        raise Exception(f"Error descargando: {e}")

# Regresa true si el archivo existe en GCS y False si no existe
def existe_archivo(ruta_gcs, nombre_bucket="tours-automaticos"):
    try:
        cliente = obtener_cliente()
        bucket = cliente.bucket(nombre_bucket)
        archivo_gcs = bucket.blob(ruta_gcs)
        
        if archivo_gcs.exists():
            return 'Encontrado'
        else:
            return 'No encontrado'
    except Exception as e:
        print(e)
        return 'Path invalido'
