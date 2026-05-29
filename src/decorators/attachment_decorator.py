"""Attachment decorator module.

Adds one or more file attachments to the email before delivery.
"""

from copy import deepcopy
from pathlib import Path
from typing import List, Union

from src.decorators.base_decorator import EmailSenderDecorator
from src.models import EmailMessage


class AttachmentDecorator(EmailSenderDecorator):
    """Decorator that attaches files from disk to the outgoing email."""

    def __init__(self, sender, attachment_paths: Union[str, Path, List[Union[str, Path]]]) -> None:
        """Initialize the attachment decorator.

        Args:
            sender: The EmailSender instance to wrap.
            attachment_paths: File path or list of paths to attach on every send.
        """
        super().__init__(sender)
        if isinstance(attachment_paths, (str, Path)):
            paths = [attachment_paths]
        else:
            paths = list(attachment_paths)
        if not paths:
            raise ValueError("attachment_paths must contain at least one file path")

        resolved: List[str] = []
        for raw_path in paths:
            path = Path(raw_path).expanduser().resolve()
            if not path.is_file():
                raise FileNotFoundError(f"Attachment file not found: {path}")
            resolved.append(str(path))
        self._attachment_paths = resolved

    def send(self, message: EmailMessage) -> bool:
        """Appends configured files to message.attachments and delegates."""
        message_copy = deepcopy(message)
        existing = {str(Path(p).resolve()) for p in message_copy.attachments}
        for path in self._attachment_paths:
            if path not in existing:
                message_copy.attachments.append(path)
                existing.add(path)
        return super().send(message_copy)
