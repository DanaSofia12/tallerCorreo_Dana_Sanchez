"""BCC (blind carbon copy) decorator module.

This module implements BccDecorator which adds hidden copy recipients
to an email before delivery, without exposing them in the visible To field.
It complies with PEP 8 and Clean Code guidelines.
"""

from copy import deepcopy
from typing import List

from src.decorators.base_decorator import EmailSenderDecorator
from src.models import EmailMessage


class BccDecorator(EmailSenderDecorator):
    """Decorator that adds blind carbon copy (BCC) recipients to the email."""

    def __init__(self, sender, bcc_recipients: List[str]) -> None:
        """Initialize the BCC decorator.

        Args:
            sender: The EmailSender instance to wrap.
            bcc_recipients: Email addresses that receive a hidden copy.
        """
        super().__init__(sender)
        if not bcc_recipients:
            raise ValueError("bcc_recipients must contain at least one address")
        self._bcc_recipients = list(bcc_recipients)

    def send(self, message: EmailMessage) -> bool:
        """Adds BCC addresses to the message and forwards to the wrapped sender."""
        message_copy = deepcopy(message)
        existing = set(message_copy.bcc)
        for address in self._bcc_recipients:
            if address not in existing:
                message_copy.bcc.append(address)
                existing.add(address)
        return super().send(message_copy)
