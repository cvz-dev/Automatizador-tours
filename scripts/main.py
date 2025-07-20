import sys

from registros_hubspot import obtener_registros_hubspot
from guardar_registros_excel import registros_excel

creado = obtener_registros_hubspot()

if creado: 
    try:
        fecha_solicitada, registros_norte, registros_sur = registros_excel()
        print(fecha_solicitada, registros_norte, registros_sur)
    except Exception:
        sys.exit(1)