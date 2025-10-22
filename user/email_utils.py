# utils/email_utils.py

import logging
from brevo_python import Configuration, ApiClient
from brevo_python.api.transactional_emails_api import TransactionalEmailsApi
from brevo_python.models.send_smtp_email import SendSmtpEmail
from django.conf import settings

logger = logging.getLogger(__name__)

def send_brevo_email(subject, text_content, from_email, to_list, html_content=None, sender_name="Atut Vidhan"):
    """
    A drop-in replacement for Django's EmailMultiAlternatives using Brevo API.

    Example:
        send_brevo_email(
            subject="Test Email",
            text_content="Plain text content",
            from_email="noreply@example.com",
            to_list=["user@example.com"],
            html_content="<p>Hello, this is a test!</p>"
        )
    """
    # === Configure Brevo client ===
    config = Configuration()
    config.api_key['api-key'] = settings.BREVO_API_KEY

    api_client = ApiClient(config)
    api_instance = TransactionalEmailsApi(api_client)

    # === Build Brevo email payload ===
    to_emails = [{"email": email} for email in to_list]
    sender_info = {"email": from_email, "name": sender_name}

    email_data = SendSmtpEmail(
        sender=sender_info,
        to=to_emails,
        subject=subject,
        html_content=html_content or text_content,
        text_content=text_content,
    )

    try:
        response = api_instance.send_transac_email(email_data)
        logger.info("✅ Email sent successfully via Brevo: %s", response)
        return True
    except Exception as e:
        logger.error("❌ Brevo email sending failed: %s", str(e), exc_info=True)
        return False
    finally:
        # Close client to release HTTP connections
        api_client.close()
