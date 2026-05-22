"""Signature decorator module.

This module implements SignatureDecorator which appends a customized
signature/footer to the email body, supporting both plain text and HTML.
It complies with PEP 8 and Clean Code guidelines.
"""

from copy import deepcopy
from src.models import EmailMessage
from src.decorators.base_decorator import EmailSenderDecorator


class SignatureDecorator(EmailSenderDecorator):
    """Decorator that automatically appends a signature or footer to the email body."""

    def __init__(self, sender, signature: str = "Enviado con tallerCorreo v1.0.0 (Patrón Decorator)") -> None:
        """Initialize the signature decorator.

        Args:
            sender: The EmailSender instance to wrap.
            signature: The signature text to append.
        """
        super().__init__(sender)
        self._signature = signature

    def send(self, message: EmailMessage) -> bool:
        """Appends the signature to the email body and forwards to the wrapped sender."""
        # Clean Code: avoid modifying the incoming message object directly to prevent side effects in callers
        message_copy = deepcopy(message)

        if message_copy.is_html:
            formatted_signature = (
                f"<br><br><hr><div style='font-family: Arial, sans-serif; "
                f"font-size: 12px; color: #555555; line-height: 1.5;'>"
                f"{self._signature.replace(chr(10), '<br>')}</div>"
            )
            # If body has </body> close tag, insert before it, otherwise append
            if "</body>" in message_copy.body.lower():
                parts = message_copy.body.rsplit("</body>", 1)
                message_copy.body = parts[0] + formatted_signature + "</body>" + parts[1]
            else:
                message_copy.body += formatted_signature
        else:
            message_copy.body += f"\n\n--\n{self._signature}"

        return super().send(message_copy)
