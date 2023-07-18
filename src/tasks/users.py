import os
import smtplib
from email.mime.text import MIMEText

from config import EMAIL_HOST_PASSWORD, EMAIl_HOST, celery_app


@celery_app.task
def send_verify_email(email: str, token: str) -> None:
    url = f'{os.getenv("domain")}/users/activate/{token}'
    msg = MIMEText(f'Link for verify your account:\n{url}')
    msg['Subject'] = 'VERIFY EMAIL'
    msg['From'] = EMAIl_HOST
    msg['To'] = email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIl_HOST, EMAIL_HOST_PASSWORD)
        server.send_message(msg)
