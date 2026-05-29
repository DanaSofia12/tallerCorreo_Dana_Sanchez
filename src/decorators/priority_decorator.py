"""Priority decorator module.

Sets standard email priority headers (X-Priority, Importance, Priority)
recognized by Gmail, Outlook, and other clients.
"""

from copy import deepcopy
from typing import Dict, Literal

from src.decorators.base_decorator import EmailSenderDecorator
from src.models import EmailMessage

EmailPriorityLevel = Literal["high", "normal", "low"]

_PRIORITY_HEADERS: Dict[EmailPriorityLevel, Dict[str, str]] = {
    "high": {
        "X-Priority": "1",
        "Importance": "high",
        "Priority": "urgent",
    },
    "normal": {
        "X-Priority": "3",
        "Importance": "normal",
        "Priority": "normal",
    },
    "low": {
        "X-Priority": "5",
        "Importance": "low",
        "Priority": "non-urgent",
    },
}


class PriorityDecorator(EmailSenderDecorator):
    """Decorator that marks the email priority via MIME headers."""

    def __init__(self, sender, priority: EmailPriorityLevel = "normal") -> None:
        """Initialize the priority decorator.

        Args:
            sender: The EmailSender instance to wrap.
            priority: One of 'high', 'normal', or 'low'.
        """
        super().__init__(sender)
        normalized = priority.lower().strip()
        if normalized not in _PRIORITY_HEADERS:
            raise ValueError(
                f"Invalid priority '{priority}'. Use: high, normal, or low."
            )
        self._priority = normalized

    @property
    def priority(self) -> EmailPriorityLevel:
        """The configured priority level."""
        return self._priority

    def send(self, message: EmailMessage) -> bool:
        """Applies priority headers to the message and delegates."""
        message_copy = deepcopy(message)
        message_copy.priority = self._priority
        for header, value in _PRIORITY_HEADERS[self._priority].items():
            message_copy.headers[header] = value
        return super().send(message_copy)
