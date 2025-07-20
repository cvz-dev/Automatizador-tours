import smtplib
import os
import ast
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def envio_registros(fecha, registros_norte, registros_sur):
    try: 
        load_dotenv()
        usuario = os.getenv('USUARIO')
        app_password = os.getenv('APP_PASSWORD')
        receptores = os.getenv('RECEPTORES')
        receptores = ast.literal_eval(receptores)
        servidor = os.getenv('SERVIDOR')
        puerto = os.getenv('PUERTO')

        # Asunto y cuerpo del email
        asunto = f"Registros tour puertas abiertas {fecha}"

        # Se define el cuerpo del correo dependiendo de si existen registros en el campus norte y sur
        if (registros_norte and registros_sur):
            cuerpo = "Buena tarde espero se encuentren de lo mejor\n" \
            "Les adjunto los registros para el tour de puertas abiertas del campus norte y sur"
        elif (registros_norte or registros_sur):
            if (registros_norte):
                cuerpo = "Buena tarde espero se encuentren de lo mejor\n" \
            "Adjunto únicamente los registros del campus norte para el tour de puertas abiertas debido a que no hay" \
            "registros disponibles para el campus sur"
            else:
                cuerpo = "Buena tarde espero se encuentren de lo mejor\n" \
            "Adjunto únicamente los registros del campus sur para el tour de puertas abiertas debido a que no hay" \
            "registros disponibles para el campus norte"
        else:
            cuerpo = "Buena tarde espero se encuentren de lo mejor\n" \
            "Escribo este correo con el fin de comentarles que no hay registros disponibles para ninguno de los dos campus" \
            "para el tour de puertas abiertas"
        
        # Se crea el objeto que va a almacenar el mensaje
        mensaje = MIMEMultipart()
        mensaje['From'] = usuario
        mensaje['To'] = ' , '.join(receptores)
        mensaje['Subject'] = asunto

        # Agregamos el cuerpo del mensaje
        mensaje.attach(MIMEText(cuerpo, 'plain', 'utf-8'))

        # Guardamos el archivo de excel con los registros
        registros_excel = "../data/registros_tours.xlsx"
        nombre_excel = os.path.basename(registros_excel)

        # Definimos si se va a adjuntar o no el archivo de excel
        if registros_norte or registros_sur:
            with open(registros_excel, "rb") as attachment:
                # Agregamos el archivo de excel
                part = MIMEBase("application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {nombre_excel}",
            )

            # Adjuntar al mensaje
            mensaje.attach(part)

        # Enviamos el correo
        with smtplib.SMTP(servidor, int(puerto)) as server:
            server.ehlo
            server.starttls()
            server.ehlo()
            server.login(usuario, app_password)
            server.sendmail(usuario, receptores, mensaje.as_string())
    
    except FileNotFoundError as desc:
        print(f"Archivo no encontrado: {desc}")
        return False
    except Exception as desc:
        print(f"Error inesperado: {str(desc)}")
        return False