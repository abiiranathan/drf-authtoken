import json
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_reset_email(request, user, subject):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject

    SITE_NAME = settings.DRF_AUTH_SETTINGS["SITE_NAME"]
    EMAIL_HOST_USER = settings.DRF_AUTH_SETTINGS["EMAIL_HOST_USER"]
    EMAIL_HOST_PASSWORD = settings.DRF_AUTH_SETTINGS["EMAIL_HOST_PASSWORD"]

    EMAIL_HOST = settings.DRF_AUTH_SETTINGS["EMAIL_HOST"]
    EMAIL_PORT = settings.DRF_AUTH_SETTINGS["EMAIL_PORT"]

    if not EMAIL_HOST or not EMAIL_PORT or not EMAIL_HOST_USER or not SITE_NAME:
        print("settings.DRF_AUTH_SETTINGS Configuration incomplete.")
        return False

    message["From"] = formataddr(
        (str(Header(SITE_NAME, "utf-8")), EMAIL_HOST_USER))
    message["To"] = user.email

    uidb64 = urlsafe_base64_encode(force_bytes(user.id))
    token = PasswordResetTokenGenerator().make_token(user)

    reset_url = request.build_absolute_uri(
        f"/api/auth/reset_password_confirmation/{uidb64}/{token}/")

    html = f"""
    <h2>Hi, {user}<h1>
    <p style="font-size: 12px; color:#333; line-height:1.6;">
    You requested for a password reset for your {SITE_NAME} account.<br>
    Please follow the link below to set your new password.<br><br>

    <a href="{reset_url}" style="background-color:teal;color: #fff;padding: 0.5rem 1rem; border-radius:8px;">Reset My Password</a>
    </p>
    """

    part1 = MIMEText(html, "html")
    message.attach(part1)

    try:
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, timeout=30) as server:
            server.ehlo()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(EMAIL_HOST_USER, user.email, message.as_string())

        return True
    except Exception as e:
        print(e)
        return False
