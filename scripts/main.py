import sys
import traceback
from registros_hubspot import obtener_registros_hubspot
from guardar_registros_excel import registros_excel
from envio_correos import envio_registros

def main():
    try:
        creado = obtener_registros_hubspot()
    except Exception as desc:
        print("❌ Error en obtener_registros_hubspot():", desc)
        traceback.print_exc()
        sys.exit(1)

    if not creado:
        print("⚠️ No se crearon registros desde HubSpot.")
        sys.exit(1)

    try:
        fecha, registros_norte, registros_sur, nombre_excel = registros_excel()
    except Exception as desc:
        print("❌ Error en registros_excel():", desc)
        traceback.print_exc()
        sys.exit(1)

    try:
        envio_registros(fecha, registros_norte, registros_sur, nombre_excel)
    except Exception as desc:
        print("❌ Error en envio_registros():", desc)
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
