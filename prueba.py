import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURACIÓN (REEMPLAZA CON TUS VALORES REALES DE GMAIL) ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USE_TLS = True
SENDER_EMAIL = "daniel1908dario@gmail.com" # Tu dirección de Gmail (MAIL_USERNAME)
SENDER_PASSWORD = "ftle hrcn tecv uiew" # ¡La contraseña de aplicación si usas 2FA!

RECEIVER_EMAIL = "2124403033@undac.edu.pe" # El correo al que quieres enviar la prueba
TEST_USERNAME = "Usuario de Prueba" # Un nombre para el correo

def send_test_email():
    try:
        # Crea el mensaje
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Prueba de Correo SMTP desde Python (Gmail)"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL

        # Contenido HTML del correo
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; margin: 0; padding: 20px; color: #333; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px; background-color: #fff; border-radius: 8px; }}
                .header {{ background-color: #0D47A1; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .code {{ font-size: 28px; font-weight: bold; text-align: center; margin: 25px 0; letter-spacing: 8px; color: #0D47A1; }}
                .footer {{ font-size: 12px; text-align: center; color: #777; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Legajo Digital - DIRESA Pasco</h2>
                </div>
                <div style="padding: 20px;">
                    <h4>Hola, {TEST_USERNAME}</h4>
                    <p>Este es un correo de prueba enviado directamente desde un script de Python.</p>
                    <div class="code">TEST12</div>
                    <p>Si recibiste este correo, la configuración SMTP es correcta.</p>
                </div>
                <div class="footer">
                    <p>Este es un correo electrónico automatizado. Por favor, no respondas.</p>
                    <p>&copy; 2025 DIRESA Pasco - Oficina de Sistemas</p>
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, "html"))

        # Conexión al servidor SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.set_debuglevel(1) # Esto mostrará la comunicación SMTP en la consola
        
        if SMTP_USE_TLS:
            server.starttls() # Inicia la encriptación TLS

        server.login(SENDER_EMAIL, SENDER_PASSWORD) # Autenticación
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string()) # Envío
        server.quit() # Cierra la conexión

        print(f"Correo de prueba enviado exitosamente a {RECEIVER_EMAIL}")

    except smtplib.SMTPAuthenticationError:
        print("ERROR: Fallo de autenticación SMTP. Verifica tu usuario y contraseña (¡y la contraseña de aplicación si usas 2FA!).")
    except smtplib.SMTPConnectError as e:
        print(f"ERROR: No se pudo conectar al servidor SMTP. Verifica MAIL_SERVER y MAIL_PORT. Detalles: {e}")
    except smtplib.SMTPException as e:
        print(f"ERROR SMTP: Ocurrió un error al enviar el correo. Detalles: {e}")
    except Exception as e:
        print(f"ERROR INESPERADO: {e}")

if __name__ == "__main__":
    send_test_email()
