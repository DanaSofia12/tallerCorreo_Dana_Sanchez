"""Interface module for the email sending system.

This module defines the abstract base class (interface) for email senders,
following the Interface Segregation and Dependency Inversion Principles (SOLID).
"""

from abc import ABC, abstractmethod
from src.models import EmailMessage


class EmailSender(ABC):
    """Abstract base class defining the contract for sending emails.

    All concrete email senders and decorators must implement this interface.
    """

    @abstractmethod
    def send(self, message: EmailMessage) -> bool:
        """Send an email message.

        Args:
            message: The EmailMessage object containing sender, recipient,
                     subject, body, and options.

        Returns:
            bool: True if the email was sent successfully, False otherwise.

        Raises:
            Exception: If an error occurs during SMTP or transport operations.
        """
        pass
