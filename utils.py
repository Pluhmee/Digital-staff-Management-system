# Utility functions (e.g., send email, export PDF/CSV)
from flask_mail import Message
from flask import current_app
from app import mail

def send_email(to, subject, body):
    msg = Message(subject, recipients=[to], body=body, sender=current_app.config['MAIL_USERNAME'])
    mail.send(msg)
