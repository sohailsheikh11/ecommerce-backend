
import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import settings


def send_email_notification(
    recipient: str,
    subject: str,
    body: str,
):
    """
    Send an email notification through Brevo SMTP.
    """

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = (
        f"{settings.smtp_from_name} "
        f"<{settings.smtp_from_email}>"
    )
    message["To"] = recipient
    message.set_content(body)

    tls_context = ssl.create_default_context()

    with smtplib.SMTP(
        settings.smtp_host,
        settings.smtp_port,
        timeout=30,
    ) as smtp:
        smtp.ehlo()
        smtp.starttls(context=tls_context)
        smtp.ehlo()

        smtp.login(
            settings.smtp_login,
            settings.smtp_key,
        )

        smtp.send_message(message)

    print(f"Email sent successfully to {recipient}")

    return True

