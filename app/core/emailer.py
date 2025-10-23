import smtplib
from email.message import EmailMessage
import os

SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "FitDojo <noreply@fitdojo.local>")

def send_email(to: str, subject: str, html: str):
    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content("HTML required")
    msg.add_alternative(html, subtype="html")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        if SMTP_USER and SMTP_PASS:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)
