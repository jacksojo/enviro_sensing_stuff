import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def send_email(content):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = os.environ['SMTP_USERNAME']
    smtp_password = os.environ['SMTP_PASSWORD']

    msg = MIMEMultipart()
    msg['From'] = os.environ['SMTP_USERNAME']
    msg['To'] = os.environ['MY_EMAIL']
    msg['Subject'] = "Temp Sensor Error"
    msg.attach(MIMEText(repr(content), 'plain'))

    # Send email
    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(os.environ['SMTP_USERNAME'], os.environ['SMTP_PASSWORD'])
        smtp.send_message(msg)
