import pandas as pd
import re
from datetime import datetime

def limpiar_fecha(fecha):
    meses = {
        'enero':"01", 'febrero':"02", 'marzo':"03", 'abril':"04", 
        'mayo':"05", 'junio':"06",'julio':"07", 'agosto':"08", 
        'septiembre':"09", 'octubre': "10", 'noviembre': "11", 'diciembre':"12" 
    }

    if pd.isna(fecha) or fecha is None:
        return pd.NaT

    if isinstance(fecha, str):
        try:
            fecha = fecha.lower()
            fecha = re.sub(r"(miércoles|miercoles|sabado|sábado)", "", fecha)
            fecha = fecha.strip()

            for key in meses:
                if re.search(key,fecha):
                    fecha = re.sub(key, meses[key], fecha)
                    break

            if not re.search(r"\b\d{4}\b", fecha):
                año_actual = datetime.now().year
                fecha = re.sub(r"(-)", f"{año_actual} -", fecha, count=1)
            else:
                fecha = re.sub(r"(\d{4})(-)", r"\1 \2", fecha)

            fecha = re.sub(r"(\d{2})(\d{4})",r"\1 \2",fecha)
            fecha = re.sub(r"(\d{1,2}:\d{2})(am|pm)", r"\1 \2", fecha)
            fecha = datetime.strptime(fecha, "%d de %m %Y - %I:%M %p")

            return fecha
        
        except Exception as desc:
            return pd.NaT
        
    return pd.NaT

#Definir una función para regresar dos DataFrames filtrados por cada campus
def filtrar_datos(ruta):

    #Lectura del archivo
    df = pd.read_csv(ruta)

    # Convertimos las columnas 'Día de visita Norte' y 'Día de visita Sur'
    # al formato datetime para poder filtrar los datos más adelante
    df['Día de visita Norte_standar'] = df['Día de visita Norte'].copy()
    df['Día de visita Sur_standar'] = df['Día de visita Sur'].copy()
    df['Día de visita Norte_standar'] = df['Día de visita Norte_standar'].apply(limpiar_fecha)
    df['Día de visita Sur_standar'] = df['Día de visita Sur_standar'].apply(limpiar_fecha)

    # Quitar las columnas relacionadas con el 'Día de visita sur'
    df_filtrado_norte = df.drop(columns=['Día de visita Sur', 'Día de visita Sur_standar'])

    # Quitar las columnas relacionadas con el 'Día de visita norte'
    df_filtrado_sur = df.drop(columns=['Día de visita Norte', 'Día de visita Norte_standar'])
     
    # Regresar dos dataframes uno por cada campus
    return df_filtrado_norte, df_filtrado_sur
