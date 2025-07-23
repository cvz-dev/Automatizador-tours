from google.cloud import storage
from google.oauth2 import service_account
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Conectarse a Google Cloud Storage
def obtener_cliente():
    load_dotenv()
    service_account_file = os.getenv("CREDENCIAL_GOOGLE")
    print("credencial cargada")
    
    credentials = service_account.Credentials.from_service_account_file(service_account_file)
    return storage.Client(credentials=credentials)

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
        print("buscar cliente")
        cliente = obtener_cliente()
        print("se obtiene el cliente")
        bucket = cliente.bucket(nombre_bucket)
        archivo_gcs = bucket.blob(ruta_gcs)
        
        if archivo_gcs.exists():
            return 'Encontrado'
        else:
            return 'No encontrado'
    except Exception as e:
        print(e)
        return 'Path invalido'