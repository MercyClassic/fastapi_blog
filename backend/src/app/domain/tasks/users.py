import os
import smtplib
from email.mime.text import MIMEText

from app.main.config import celery_app


@celery_app.task
def send_verify_email(email: str, token: str) -> None:
    email_host = os.environ['EMAIl_HOST']
    email_password = os.environ['EMAIL_PASSWORD']
    url = f'{os.getenv("domain")}/users/activate/{token}'
    msg = MIMEText(f'Link for verify your account:\n{url}')
    msg['Subject'] = 'VERIFY EMAIL'
    msg['From'] = email_host
    msg['To'] = email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(email_host, email_password)
        server.send_message(msg)
