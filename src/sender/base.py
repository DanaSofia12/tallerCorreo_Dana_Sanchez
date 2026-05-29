"""Base email sender module.

This module implements the concrete EmailSender using standard smtplib,
supporting both real sending and local development simulations.
It complies with PEP 8 and Clean Code guidelines.
"""

import datetime
import mimetypes
import smtplib
from email import encoders
from email.mime.base import MIMEBase
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
            if message.bcc:
                f.write(f"Bcc: {', '.join(message.bcc)}\n")
            f.write(f"Subject: {message.subject}\n")
            for k, v in message.headers.items():
                f.write(f"{k}: {v}\n")
            f.write(f"Format: {'HTML' if message.is_html else 'Plain Text'}\n")
            if message.priority:
                f.write(f"Priority: {message.priority}\n")
            if message.attachments:
                f.write(f"Attachments: {', '.join(message.attachments)}\n")
            f.write("-------------------------------\n\n")
            f.write(message.body)
            if message.attachments:
                f.write("\n\n--- ATTACHED FILES (simulated) ---\n")
                for attachment_path in message.attachments:
                    path = Path(attachment_path)
                    f.write(f"\n[{path.name}]\n")
                    f.write(path.read_text(encoding="utf-8", errors="replace"))

        # Print clean preview to stdout
        print("\n" + "=" * 50)
        print(" [SIMULATED EMAIL SENT SUCCESSFULLY] ")
        print(f"  To:       {message.recipient}")
        if message.bcc:
            print(f"  Bcc:      {', '.join(message.bcc)}")
        print(f"  Subject:  {message.subject}")
        if message.priority:
            print(f"  Priority: {message.priority}")
        if message.attachments:
            print(f"  Files:    {', '.join(Path(p).name for p in message.attachments)}")
        print(f"  Saved to: {file_path.relative_to(config.BASE_DIR)}")
        print("=" * 50 + "\n")
        return True

    def _build_mime_message(self, message: EmailMessage) -> MIMEMultipart:
        """Builds a MIME message with body, optional attachments, and headers."""
        if message.attachments:
            mime_msg: MIMEMultipart = MIMEMultipart("mixed")
            body_container = MIMEMultipart("alternative")
            body_container.attach(
                MIMEText(message.body, "html" if message.is_html else "plain", "utf-8")
            )
            mime_msg.attach(body_container)
            for attachment_path in message.attachments:
                mime_msg.attach(self._build_attachment_part(attachment_path))
        else:
            mime_msg = MIMEMultipart("alternative")
            mime_msg.attach(
                MIMEText(message.body, "html" if message.is_html else "plain", "utf-8")
            )

        mime_msg["From"] = message.sender
        mime_msg["To"] = message.recipient
        mime_msg["Subject"] = message.subject
        if message.bcc:
            mime_msg["Bcc"] = ", ".join(message.bcc)
        for key, value in message.headers.items():
            mime_msg[key] = value
        return mime_msg

    @staticmethod
    def _build_attachment_part(attachment_path: str) -> MIMEBase:
        """Creates a MIME part for a file attachment."""
        path = Path(attachment_path)
        mime_type, _ = mimetypes.guess_type(path.name)
        if mime_type:
            maintype, subtype = mime_type.split("/", 1)
        else:
            maintype, subtype = "application", "octet-stream"

        with open(path, "rb") as attachment_file:
            part = MIMEBase(maintype, subtype)
            part.set_payload(attachment_file.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            "attachment",
            filename=path.name,
        )
        return part

    def _send_real(self, message: EmailMessage) -> bool:
        """Sends a real email using SMTP protocol."""
        mime_msg = self._build_mime_message(message)

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

            all_recipients = [message.recipient, *message.bcc]
            server.sendmail(message.sender, all_recipients, mime_msg.as_string())
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
