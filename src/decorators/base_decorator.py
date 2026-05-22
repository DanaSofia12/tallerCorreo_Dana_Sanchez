"""Base decorator module.

This module defines the abstract base decorator for all email senders,
following the Decorator pattern. It implements EmailSender and wraps
another EmailSender instance. It complies with PEP 8 and SOLID.
"""

from src.models import EmailMessage
from src.sender.interface import EmailSender


class EmailSenderDecorator(EmailSender):
    """Abstract base decorator class.

    It delegates the send operation to the wrapped EmailSender instance.
    """

    def __init__(self, sender: EmailSender) -> None:
        """Initialize the decorator with a wrapped email sender.

        Args:
            sender: The EmailSender instance to wrap.
        """
        self._wrapped = sender

    def send(self, message: EmailMessage) -> bool:
        """Delegate the sending process to the wrapped sender.

        Decorators can override this method to add custom behavior
        before and/or after calling the wrapped sender.
        """
        return self._wrapped.send(message)
