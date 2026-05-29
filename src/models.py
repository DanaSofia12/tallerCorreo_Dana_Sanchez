"""Models module for the email sending system.

This module contains data models that represent email components, complying with
Clean Code and SOLID principles (Single Responsibility Principle).
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class EmailMessage:
    """Class representing an email message (Single Responsibility: Holds email data)."""

    sender: str
    recipient: str
    subject: str
    body: str
    is_html: bool = False
    bcc: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    priority: Optional[str] = None
    headers: dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate input values to ensure data integrity."""
        if not self.sender or "@" not in self.sender:
            raise ValueError(f"Invalid sender address: '{self.sender}'")
        if not self.recipient or "@" not in self.recipient:
            raise ValueError(f"Invalid recipient address: '{self.recipient}'")
        if not self.subject.strip():
            raise ValueError("Subject cannot be empty or only whitespace")
        for address in self.bcc:
            if not address or "@" not in address:
                raise ValueError(f"Invalid BCC address: '{address}'")
