"""Unit tests for the email sending system and its decorators.

This module validates that the models, sender, and decorators behave correctly
both in isolation and when combined, complying with PEP 8 and Clean Code.
"""

import unittest
from unittest.mock import MagicMock

from src.models import EmailMessage
import tempfile
from pathlib import Path

from src.decorators.attachment_decorator import AttachmentDecorator
from src.decorators.bcc_decorator import BccDecorator
from src.decorators.logging_decorator import LoggingDecorator
from src.decorators.priority_decorator import PriorityDecorator
from src.decorators.signature_decorator import SignatureDecorator
from src.decorators.html_decorator import HtmlWrapperDecorator
from src.decorators.retry_decorator import RetryDecorator


class TestEmailMessage(unittest.TestCase):
    """Test case for EmailMessage model validations."""

    def test_valid_email_message(self):
        """Should successfully create a valid email message."""
        msg = EmailMessage(
            sender="sender@example.com",
            recipient="recipient@example.com",
            subject="Test Subject",
            body="Test Body"
        )
        self.assertEqual(msg.sender, "sender@example.com")
        self.assertEqual(msg.recipient, "recipient@example.com")
        self.assertEqual(msg.subject, "Test Subject")
        self.assertEqual(msg.body, "Test Body")
        self.assertFalse(msg.is_html)

    def test_invalid_sender_raises_value_error(self):
        """Should raise ValueError if sender email is invalid."""
        with self.assertRaises(ValueError):
            EmailMessage(
                sender="invalid-email",
                recipient="recipient@example.com",
                subject="Test",
                body="Test"
            )

    def test_invalid_recipient_raises_value_error(self):
        """Should raise ValueError if recipient email is invalid."""
        with self.assertRaises(ValueError):
            EmailMessage(
                sender="sender@example.com",
                recipient="invalid-email",
                subject="Test",
                body="Test"
            )

    def test_empty_subject_raises_value_error(self):
        """Should raise ValueError if subject is empty or spaces."""
        with self.assertRaises(ValueError):
            EmailMessage(
                sender="sender@example.com",
                recipient="recipient@example.com",
                subject="   ",
                body="Test"
            )


class TestSignatureDecorator(unittest.TestCase):
    """Test case for SignatureDecorator."""

    def setUp(self):
        self.mock_sender = MagicMock()
        self.decorator = SignatureDecorator(self.mock_sender, signature="My Signature")

    def test_signature_plain_text(self):
        """Should append plain text signature to a plain text body."""
        msg = EmailMessage(
            sender="sender@example.com",
            recipient="recipient@example.com",
            subject="Plain text",
            body="Hello World"
        )
        self.decorator.send(msg)

        # Verify wrapped sender is called with modified message
        self.mock_sender.send.assert_called_once()
        modified_msg = self.mock_sender.send.call_args[0][0]
        self.assertEqual(modified_msg.body, "Hello World\n\n--\nMy Signature")
        self.assertFalse(modified_msg.is_html)

    def test_signature_html(self):
        """Should insert HTML signature inside the body of an HTML email."""
        msg = EmailMessage(
            sender="sender@example.com",
            recipient="recipient@example.com",
            subject="HTML email",
            body="<html><body>Hello HTML</body></html>",
            is_html=True
        )
        self.decorator.send(msg)

        self.mock_sender.send.assert_called_once()
        modified_msg = self.mock_sender.send.call_args[0][0]
        self.assertIn("My Signature", modified_msg.body)
        self.assertIn("</body>", modified_msg.body)
        self.assertTrue(modified_msg.is_html)


class TestHtmlWrapperDecorator(unittest.TestCase):
    """Test case for HtmlWrapperDecorator."""

    def setUp(self):
        self.mock_sender = MagicMock()
        self.decorator = HtmlWrapperDecorator(
            self.mock_sender,
            theme_color="#123456",
            company_name="Test Company"
        )

    def test_wraps_plain_text_into_html(self):
        """Should convert a plain text email to a styled HTML structure."""
        msg = EmailMessage(
            sender="sender@example.com",
            recipient="recipient@example.com",
            subject="Wrap Me",
            body="Plain email text"
        )
        self.decorator.send(msg)

        self.mock_sender.send.assert_called_once()
        modified_msg = self.mock_sender.send.call_args[0][0]
        self.assertTrue(modified_msg.is_html)
        self.assertIn("<!DOCTYPE html>", modified_msg.body)
        self.assertIn("Plain email text", modified_msg.body)
        self.assertIn("#123456", modified_msg.body)
        self.assertIn("Test Company", modified_msg.body)

    def test_does_not_wrap_existing_html(self):
        """Should not wrap an email if it is already HTML."""
        existing_html = "<html><body>Already HTML</body></html>"
        msg = EmailMessage(
            sender="sender@example.com",
            recipient="recipient@example.com",
            subject="Don't Wrap",
            body=existing_html,
            is_html=True
        )
        self.decorator.send(msg)

        self.mock_sender.send.assert_called_once()
        modified_msg = self.mock_sender.send.call_args[0][0]
        self.assertEqual(modified_msg.body, existing_html)
        self.assertTrue(modified_msg.is_html)


class TestBccDecorator(unittest.TestCase):
    """Test case for BccDecorator."""

    def setUp(self):
        self.mock_sender = MagicMock()
        self.decorator = BccDecorator(
            self.mock_sender,
            bcc_recipients=["audit@example.com", "archive@example.com"],
        )

    def test_adds_bcc_recipients(self):
        """Should append BCC addresses before delegating to the wrapped sender."""
        msg = EmailMessage(
            sender="sender@example.com",
            recipient="recipient@example.com",
            subject="BCC Test",
            body="Hello",
        )
        self.decorator.send(msg)

        self.mock_sender.send.assert_called_once()
        modified_msg = self.mock_sender.send.call_args[0][0]
        self.assertEqual(
            modified_msg.bcc,
            ["audit@example.com", "archive@example.com"],
        )
        self.assertEqual(msg.bcc, [])

    def test_merges_without_duplicates(self):
        """Should not duplicate BCC entries already present on the message."""
        msg = EmailMessage(
            sender="sender@example.com",
            recipient="recipient@example.com",
            subject="BCC Test",
            body="Hello",
            bcc=["audit@example.com"],
        )
        self.decorator.send(msg)

        modified_msg = self.mock_sender.send.call_args[0][0]
        self.assertEqual(
            modified_msg.bcc,
            ["audit@example.com", "archive@example.com"],
        )

    def test_empty_bcc_list_raises_value_error(self):
        """Should reject construction without at least one BCC address."""
        with self.assertRaises(ValueError):
            BccDecorator(self.mock_sender, bcc_recipients=[])


class TestRetryDecorator(unittest.TestCase):
    """Test case for RetryDecorator."""

    def test_successful_on_first_try(self):
        """Should send successfully without retrying if no exception is raised."""
        mock_sender = MagicMock()
        mock_sender.send.return_value = True
        decorator = RetryDecorator(mock_sender, retries=2, delay=0.01)

        msg = EmailMessage(
            sender="sender@example.com",
            recipient="recipient@example.com",
            subject="Test",
            body="Test"
        )
        result = decorator.send(msg)

        self.assertTrue(result)
        mock_sender.send.assert_called_once_with(msg)

    def test_retries_on_failure_and_succeeds(self):
        """Should retry and succeed on the second attempt."""
        mock_sender = MagicMock()
        mock_sender.send.side_effect = [RuntimeError("Connection failed"), True]
        # Short delay for fast unit tests
        decorator = RetryDecorator(mock_sender, retries=2, delay=0.01, backoff_factor=1.0)

        msg = EmailMessage(
            sender="sender@example.com",
            recipient="recipient@example.com",
            subject="Test",
            body="Test"
        )
        result = decorator.send(msg)

        self.assertTrue(result)
        self.assertEqual(mock_sender.send.call_count, 2)

    def test_eventually_fails_after_max_retries(self):
        """Should attempt sending the maximum number of times and then propagate the exception."""
        mock_sender = MagicMock()
        mock_sender.send.side_effect = RuntimeError("Persistent SMTP Error")
        decorator = RetryDecorator(mock_sender, retries=3, delay=0.01, backoff_factor=1.0)

        msg = EmailMessage(
            sender="sender@example.com",
            recipient="recipient@example.com",
            subject="Test",
            body="Test"
        )

        with self.assertRaises(RuntimeError):
            decorator.send(msg)

        # 1 initial try + 3 retries = 4 calls total
        self.assertEqual(mock_sender.send.call_count, 4)


class TestAttachmentDecorator(unittest.TestCase):
    """Test case for AttachmentDecorator."""

    def setUp(self):
        self.mock_sender = MagicMock()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.sample_file = Path(self.temp_dir.name) / "sample.txt"
        self.sample_file.write_text("attachment content", encoding="utf-8")
        self.decorator = AttachmentDecorator(
            self.mock_sender,
            attachment_paths=str(self.sample_file),
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_adds_attachment_path(self):
        """Should append the configured file to message.attachments."""
        msg = EmailMessage(
            sender="sender@example.com",
            recipient="recipient@example.com",
            subject="Attachment Test",
            body="Hello",
        )
        self.decorator.send(msg)

        modified_msg = self.mock_sender.send.call_args[0][0]
        self.assertEqual(modified_msg.attachments, [str(self.sample_file.resolve())])
        self.assertEqual(msg.attachments, [])

    def test_missing_file_raises_file_not_found(self):
        """Should reject construction when the file does not exist."""
        with self.assertRaises(FileNotFoundError):
            AttachmentDecorator(self.mock_sender, attachment_paths="/no/existe.txt")


class TestPriorityDecorator(unittest.TestCase):
    """Test case for PriorityDecorator."""

    def setUp(self):
        self.mock_sender = MagicMock()

    def test_high_priority_headers(self):
        """Should set high-priority MIME headers."""
        decorator = PriorityDecorator(self.mock_sender, priority="high")
        msg = EmailMessage(
            sender="sender@example.com",
            recipient="recipient@example.com",
            subject="Priority Test",
            body="Hello",
        )
        decorator.send(msg)

        modified_msg = self.mock_sender.send.call_args[0][0]
        self.assertEqual(modified_msg.priority, "high")
        self.assertEqual(modified_msg.headers["X-Priority"], "1")
        self.assertEqual(modified_msg.headers["Importance"], "high")
        self.assertEqual(modified_msg.headers["Priority"], "urgent")

    def test_invalid_priority_raises_value_error(self):
        """Should reject unknown priority values."""
        with self.assertRaises(ValueError):
            PriorityDecorator(self.mock_sender, priority="urgent")


class TestDecoratorPipelineIntegration(unittest.TestCase):
    """Integration test case verifying multiple decorators chained together."""

    def test_pipeline_integration(self):
        """Should successfully run a message through all decorators in sequence."""
        mock_base_sender = MagicMock()
        mock_base_sender.send.return_value = True

        with tempfile.TemporaryDirectory() as temp_dir:
            attachment_file = Path(temp_dir) / "pipeline.txt"
            attachment_file.write_text("pipeline attachment", encoding="utf-8")

            # Pipeline: Logging -> Retry -> Bcc -> Priority -> Attachment -> Signature -> Html -> Base
            pipeline = LoggingDecorator(
                RetryDecorator(
                    BccDecorator(
                        PriorityDecorator(
                            AttachmentDecorator(
                                SignatureDecorator(
                                    HtmlWrapperDecorator(
                                        mock_base_sender,
                                        theme_color="#333",
                                        company_name="Pipeline Co.",
                                    ),
                                    signature="Integrated Signature",
                                ),
                                attachment_paths=str(attachment_file),
                            ),
                            priority="high",
                        ),
                        bcc_recipients=["bcc@example.com"],
                    ),
                    retries=1,
                    delay=0.01,
                )
            )

            msg = EmailMessage(
                sender="sender@example.com",
                recipient="recipient@example.com",
                subject="Pipeline Test",
                body="Base message content"
            )

            result = pipeline.send(msg)

            self.assertTrue(result)
            mock_base_sender.send.assert_called_once()

            final_msg = mock_base_sender.send.call_args[0][0]
            self.assertTrue(final_msg.is_html)
            self.assertIn("<!DOCTYPE html>", final_msg.body)
            self.assertIn("Base message content", final_msg.body)
            self.assertIn("Integrated Signature", final_msg.body)
            self.assertIn("Pipeline Co.", final_msg.body)
            self.assertEqual(final_msg.bcc, ["bcc@example.com"])
            self.assertEqual(final_msg.priority, "high")
            self.assertEqual(final_msg.headers["Importance"], "high")
            self.assertEqual(final_msg.attachments, [str(attachment_file.resolve())])


if __name__ == "__main__":
    unittest.main()
