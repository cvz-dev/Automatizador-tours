import sys
from registros_hubspot import obtener_registros_hubspot
from guardar_registros_excel import registros_excel
from envio_correos import envio_registros

def main():

    try :
        creado = obtener_registros_hubspot()
    except Exception as desc:
        print(desc)
        sys.exit(1)

    if not creado: 
        sys.exit(1)

    try:
        fecha, registros_norte, registros_sur, nombre_excel = registros_excel()

    except Exception as desc:
        print(desc)
        sys.exit(1)

    try:
        envio_registros(fecha, registros_norte, registros_sur, nombre_excel)
    except Exception as desc:
        print(desc)
        sys.Exit(1)

if __name__ == '__main__':
    main()