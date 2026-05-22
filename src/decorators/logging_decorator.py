"""Logging decorator module.

This module implements LoggingDecorator which adds auditing and execution logs
to any EmailSender implementation. It complies with PEP 8 and Clean Code guidelines.
"""

import logging
import time

import config
from src.models import EmailMessage
from src.decorators.base_decorator import EmailSenderDecorator

# Setup logging config
log_file = config.LOGS_DIR / "email_system.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("EmailLogger")


class LoggingDecorator(EmailSenderDecorator):
    """Decorator that adds logging and performance measurement to the email sending operation."""

    def send(self, message: EmailMessage) -> bool:
        """Sends the email, logging details before and after execution."""
        logger.info("Initiating email send operation to: %s", message.recipient)
        if message.bcc:
            logger.info("BCC (hidden copy): %s", ", ".join(message.bcc))
        logger.info("Subject: '%s' | Sender: %s", message.subject, message.sender)

        start_time = time.perf_counter()
        try:
            success = super().send(message)
            elapsed_time = (time.perf_counter() - start_time) * 1000

            if success:
                logger.info(
                    "SUCCESS: Email to %s sent successfully. Duration: %.2fms",
                    message.recipient, elapsed_time
                )
            else:
                logger.warning(
                    "WARNING: Email to %s completed with failure status. Duration: %.2fms",
                    message.recipient, elapsed_time
                )
            return success
        except Exception as e:
            elapsed_time = (time.perf_counter() - start_time) * 1000
            logger.error(
                "ERROR: Email send to %s failed with exception: %s. Duration: %.2fms",
                message.recipient, e, elapsed_time, exc_info=True
            )
            raise
