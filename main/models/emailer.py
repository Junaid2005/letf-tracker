"""File that handles the emailing functionality"""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.logger import logger  # pylint: disable=wrong-import-position


def send_email(sender_email, sender_password, html_table):
    """Send an email with table output to yourself"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Dashboard Summary"
    msg["From"] = sender_email
    msg["To"] = sender_email
    msg.attach(MIMEText(html_table, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, sender_email, msg.as_string())
    logger.logger.info("Successfully sent email")
