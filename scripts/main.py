import sys
import traceback
from registros_hubspot import obtener_registros_hubspot
from guardar_registros_excel import registros_excel
from envio_correos import envio_registros
from datetime import datetime

def main():
    fecha_solicitada = None #datetime(2025, 7, 30).date()

    try:
        print("Inicia hubspot")
        creado = obtener_registros_hubspot()
        print("Termina hubspot")
    except Exception as desc:
        print("Error en obtener_registros_hubspot():", desc)
        traceback.print_exc()
        sys.exit(1)

    if not creado:
        print("No se crearon registros desde HubSpot.")
        sys.exit(1)

    try:
        print("Inicia excel")
        fecha, registros_norte, registros_sur, nombre_excel = registros_excel(fecha_solicitada)
        print("Termina excel")
    except Exception as desc:
        print("Error en registros_excel():", desc)
        traceback.print_exc()
        sys.exit(1)

    try:
        print("Inicia correo")
        envio_registros(fecha, registros_norte, registros_sur, nombre_excel)
        print("Termina correo")
    except Exception as desc:
        print("Error en envio_registros():", desc)
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
