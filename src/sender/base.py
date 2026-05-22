"""Base email sender module.

This module implements the concrete EmailSender using standard smtplib,
supporting both real sending and local development simulations.
It complies with PEP 8 and Clean Code guidelines.
"""

import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import config
from src.models import EmailMessage
from src.sender.interface import EmailSender


class BaseEmailSender(EmailSender):
    """Concrete implementation of EmailSender using SMTP protocol.

    Follows SRP (Single Responsibility: Transmitting the email bytes over SMTP).
    """

    def send(self, message: EmailMessage) -> bool:
        """Sends the email message.

        If SMTP_SIMULATION is enabled in config, it writes the email contents
        to a file and prints to stdout instead of calling SMTP servers.
        """
        if config.SMTP_SIMULATION:
            return self._send_simulated(message)
        return self._send_real(message)

    def _send_simulated(self, message: EmailMessage) -> bool:
        """Simulates sending an email by writing it to console and file."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        ext = "html" if message.is_html else "txt"
        file_path = config.OUTPUT_DIR / f"email_{timestamp}_{message.recipient}.{ext}"

        # Write to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("--- SIMULATED EMAIL HEADERS ---\n")
            f.write(f"From: {message.sender}\n")
            f.write(f"To: {message.recipient}\n")
            f.write(f"Subject: {message.subject}\n")
            for k, v in message.headers.items():
                f.write(f"{k}: {v}\n")
            f.write(f"Format: {'HTML' if message.is_html else 'Plain Text'}\n")
            f.write("-------------------------------\n\n")
            f.write(message.body)

        # Print clean preview to stdout
        print("\n" + "=" * 50)
        print(" [SIMULATED EMAIL SENT SUCCESSFULLY] ")
        print(f"  To:       {message.recipient}")
        print(f"  Subject:  {message.subject}")
        print(f"  Saved to: {file_path.relative_to(config.BASE_DIR)}")
        print("=" * 50 + "\n")
        return True

    def _send_real(self, message: EmailMessage) -> bool:
        """Sends a real email using SMTP protocol."""
        # Create message container
        mime_msg = MIMEMultipart("alternative")
        mime_msg["From"] = message.sender
        mime_msg["To"] = message.recipient
        mime_msg["Subject"] = message.subject

        # Add custom headers if any
        for k, v in message.headers.items():
            mime_msg[k] = v

        # Record the MIME types of both parts - text/plain and text/html.
        part = MIMEText(message.body, "html" if message.is_html else "plain", "utf-8")
        mime_msg.attach(part)

        # Connect to server
        server = None
        try:
            if config.SMTP_USE_TLS:
                server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT)

            # Log in if password is provided
            if config.SMTP_PASSWORD:
                server.login(config.SMTP_USER, config.SMTP_PASSWORD)

            server.sendmail(message.sender, message.recipient, mime_msg.as_string())
            return True
        except Exception as e:
            # Re-raise to let decorators handle or report the issue
            raise RuntimeError(f"SMTP sending failed: {e}") from e
        finally:
            if server:
                try:
                    server.quit()
                except Exception:
                    pass
