"""Retry decorator module.

This module implements RetryDecorator which automatically retries sending
an email in case of transient exceptions, providing robustness.
It complies with PEP 8 and Clean Code guidelines.
"""

import time
import logging
from src.models import EmailMessage
from src.decorators.base_decorator import EmailSenderDecorator

logger = logging.getLogger("EmailLogger")


class RetryDecorator(EmailSenderDecorator):
    """Decorator that implements a retry mechanism with exponential backoff for sending emails."""

    def __init__(self, sender, retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0) -> None:
        """Initialize the retry decorator.

        Args:
            sender: The EmailSender instance to wrap.
            retries: Max number of retries.
            delay: Initial delay between retries in seconds.
            backoff_factor: Multiplier for backoff delay.
        """
        super().__init__(sender)
        self._retries = retries
        self._delay = delay
        self._backoff_factor = backoff_factor

    def send(self, message: EmailMessage) -> bool:
        """Sends the email and automatically retries if a transient exception is raised."""
        attempt = 1
        current_delay = self._delay

        while True:
            try:
                return super().send(message)
            except Exception as e:
                if attempt > self._retries:
                    logger.error(
                        "RETRY FAILED: Maximum retry attempts (%d) reached. "
                        "Propagating error: %s",
                        self._retries, e
                    )
                    raise

                logger.warning(
                    "SEND FAILED (Attempt %d/%d): %s. "
                    "Retrying in %.2f seconds...",
                    attempt, self._retries + 1, e, current_delay
                )
                time.sleep(current_delay)
                attempt += 1
                current_delay *= self._backoff_factor
