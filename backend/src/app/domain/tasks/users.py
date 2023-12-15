import os
import smtplib
from email.mime.text import MIMEText

from app.main.config import celery_app, get_settings


@celery_app.task
def send_verify_email(email: str, token: str) -> None:
    settings = get_settings()
    url = f'{os.getenv("domain")}/users/activate/{token}'
    msg = MIMEText(f'Link for verify your account:\n{url}')
    msg['Subject'] = 'VERIFY EMAIL'
    msg['From'] = settings.EMAIl_HOST
    msg['To'] = email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(settings.EMAIl_HOST, settings.EMAIL_HOST_PASSWORD)
        server.send_message(msg)
