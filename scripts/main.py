import sys

from registros_hubspot import obtener_registros_hubspot
from guardar_registros_excel import registros_excel

creado = obtener_registros_hubspot()

if creado: 
    try:
        registros_excel()
    except Exception:
        sys.exit(1)
