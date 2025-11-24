# email_utils.py

import threading
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings


class EmailHelper:
    """
    Generic async email sender using Django's EmailMultiAlternatives.
    Uses settings.py backend & credentials (SMTP, Brevo, Resend via SMTP etc.)
    """

    @staticmethod
    def _send_email(subject, to, html_content, text_content, from_email):
        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=to,
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)
            print(f"[Email] Sent to {to}")
        except Exception as e:
            print(f"[Email Error] Failed for {to}: {e}")

    @staticmethod
    def send_email(
        subject: str,
        to,
        html_content: str,
        text_content: str = None,
        from_email: str = None,
        async_send: bool = True,
    ):
        """
        Sends an email. Always async by default.
        """

        if isinstance(to, str):
            to = [to]

        from_email = from_email or settings.DEFAULT_FROM_EMAIL
        text_content = text_content or strip_tags(html_content)

        # Spawn async thread
        if async_send:
            threading.Thread(
                target=EmailHelper._send_email,
                args=(subject, to, html_content, text_content, from_email),
                daemon=True
            ).start()
            return {"success": True, "async": True}

        # Sync fallback
        EmailHelper._send_email(subject, to, html_content, text_content, from_email)
        return {"success": True, "async": False}


# Convenience wrapper functions
def send_html_email(subject, to, html_content, text_content=None, from_email=None):
    return EmailHelper.send_email(
        subject=subject,
        to=to,
        html_content=html_content,
        text_content=text_content,
        from_email=from_email,
        async_send=True,  # always async
    )
