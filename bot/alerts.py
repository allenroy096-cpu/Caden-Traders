# Sends alerts and notifications

import smtplib
from email.mime.text import MIMEText
import os

def send_email_alert(subject, body, to_email):
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.example.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER', 'user@example.com')
    smtp_pass = os.getenv('SMTP_PASS', 'password')
    from_email = smtp_user
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(from_email, [to_email], msg.as_string())
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Email alert error: {e}")

def send_alert(message, channel='print'):
    if channel == 'email':
        # Example usage: send_email_alert('Trade Alert', message, 'your@email.com')
        pass
    else:
        print(f"ALERT: {message}")
