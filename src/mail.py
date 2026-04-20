import smtplib
import ssl
from email.message import EmailMessage
from src.ui import print_log, MAIL_ENABLED, print_error

import config
MAIL_PSWD = getattr(config, 'MAIL_PSWD', None)
MAIL = getattr(config, 'MAIL', None)

def send_email(message):
    if MAIL_ENABLED:
        # config
        sender_email = MAIL
        receiver_email = MAIL
        password = MAIL_PSWD

        # email
        msg = EmailMessage()
        msg['Subject'] = "Rename (python script)"
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg.set_content(f"""\
        {message}
        """)

        # send
        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2

        print_log("Connecting to server...")
        try:
            # Use Gmail's SMTP server on port 465 for SSL
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.send_message(msg)
                print_log("Success: Email sent successfully!")
                
        except smtplib.SMTPAuthenticationError as e:
            raise RuntimeError(print_error(" ❌ Error: Authentication failed. Check your email and password",e))
        except Exception as e:
            raise RuntimeError(print_error(" ❌ Error: An unexpected error occurred while trying to send an email",e))
    else:
        return