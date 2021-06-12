import atexit
import logging
import os
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import (
    SMTP,
    SMTPAuthenticationError,
    SMTPException,
    SMTPHeloError,
    SMTPNotSupportedError,
)
from typing import Optional

try:
    from .feed import Feed  # imported for type hinting
except ImportError:
    pass

DEFAULT_EMAIL_SERVER = "smtp.gmail.com"
CUSTOM_EMAIL_SERVER: Optional[str] = None


def get_email_server() -> str:
    if CUSTOM_EMAIL_SERVER:
        return CUSTOM_EMAIL_SERVER
    return os.environ.get("FEED_EMAIL_SERVER", DEFAULT_EMAIL_SERVER)


def set_email_server(server_url: str) -> None:
    global CUSTOM_EMAIL_SERVER
    CUSTOM_EMAIL_SERVER = server_url


class ServerError(Exception):
    pass


def create_server(server_url: str, email: str, password: str) -> SMTP:
    context = ssl.create_default_context()
    server = SMTP(server_url, 587)

    try:
        server.starttls(context=context)
        server.login(email, password)
    except (
        SMTPHeloError,
        SMTPException,
        SMTPNotSupportedError,
        SMTPAuthenticationError,
    ) as error:
        logging.error(error)
        server.quit()
        raise ServerError

    atexit.register(lambda: server.quit())
    return server


class FeedMailer:
    def __init__(self, subject: str, should_send: bool, email: str):
        self.subject = subject
        self.should_send = should_send
        self.email = email

    def __call__(
        self,
        smtp_server: SMTP,
        recepient_email: str,
        force_send: bool = False,
        dry_run: bool = False,
    ) -> bool:
        def _build_message() -> str:
            message = MIMEMultipart()
            message["From"] = f"Feed Mailer <{smtp_server.user}>"
            message["To"] = recepient_email
            message["Subject"] = f"Feed: {self.subject}"
            message.attach((MIMEText(self.email, "html")))
            return message.as_string()

        if self.should_send or force_send:
            message = _build_message()

            logging.debug("Email")
            logging.debug(message)

            if not dry_run:
                smtp_server.sendmail(smtp_server.user, recepient_email, message)
                return True
        return False
