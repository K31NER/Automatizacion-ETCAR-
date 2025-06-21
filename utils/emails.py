import os
from dotenv import load_dotenv
from fastapi_mail import FastMail,MessageSchema,ConnectionConfig

load_dotenv()

# Definimos las configuraciones de correo
Email = os.getenv("CORREO")
Password = os.getenv("CODIGO")

# Configuracion de el email
conf = ConnectionConfig(
    MAIL_USERNAME=Email,
    MAIL_PASSWORD=Password,
    MAIL_FROM=Email,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def enviar_correo_creacion(data:dict,destinario:str):
    """ Envia un correo a los nuevos usuarios registrados"""
    
    user_email, user_password,username = data.get("email"), data.get("password"),data.get("username")
    
    with open("templates/email_welcome.html", "r", encoding="utf-8") as file:
        html_content = file.read()
        
    # Reemplazar placeholders
    html_content = html_content.replace("{{email}}", user_email)
    html_content = html_content.replace("{{password}}", user_password)
    html_content = html_content.replace("{{username}}", username)
    
    # Definimos el mensaje
    mensaje = MessageSchema(
        subject=f"Bienvenido {username}",
        recipients=[destinario],
        body=html_content,
        subtype="html"
    )
    
    # Enviamos el mensaje
    fm = FastMail(config=conf)
    await fm.send_message(mensaje)
    

async def enviar_correo_eliminacion(username,destinario:str):
    """ Envia un correo para notificar de eliminacion de cuenta"""
    
    #leemos el html
    with open("templates/email_farewell.html", "r", encoding="utf-8") as file:
        html_content = file.read()
        
    # Reemplazar placeholders
    html_content = html_content.replace("{{username}}", username)
    
    # Definimos el mensaje
    mensaje = MessageSchema(
        subject=f"Gracias por tus servicios {username}",
        recipients=[destinario],
        body=html_content,
        subtype="html"
    )
    
    # Enviamos el mensaje
    fm = FastMail(config=conf)
    await fm.send_message(mensaje)