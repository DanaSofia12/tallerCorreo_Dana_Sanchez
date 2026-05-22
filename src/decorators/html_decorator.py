"""HTML formatting decorator module.

This module implements HtmlWrapperDecorator which wraps plain text email bodies
in a modern, premium HTML template with rich aesthetics.
It complies with PEP 8 and Clean Code guidelines.
"""

import datetime
from copy import deepcopy
import html
from src.models import EmailMessage
from src.decorators.base_decorator import EmailSenderDecorator


class HtmlWrapperDecorator(EmailSenderDecorator):
    """Decorator that wraps a plain text email in a high-quality HTML template."""

    def __init__(self, sender, theme_color: str = "#4f46e5", company_name: str = "Taller Correo Inc.") -> None:
        """Initialize the HTML wrapper decorator.

        Args:
            sender: The EmailSender instance to wrap.
            theme_color: Hex color string for the template header and branding.
            company_name: The company name used in the template footer.
        """
        super().__init__(sender)
        self._theme_color = theme_color
        self._company_name = company_name

    def send(self, message: EmailMessage) -> bool:
        """Wraps the plain text body into an HTML layout, then forwards to the wrapped sender."""
        message_copy = deepcopy(message)

        # Only wrap if it is not already marked as HTML
        if not message_copy.is_html:
            escaped_body = html.escape(message_copy.body).replace("\n", "<br>")
            current_year = datetime.datetime.now().year

            # Create an aesthetic, responsive HTML container
            html_body = (
                f"<!DOCTYPE html>\n"
                f"<html>\n"
                f"<head>\n"
                f"    <meta charset=\"utf-8\">\n"
                f"    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
                f"    <title>{html.escape(message_copy.subject)}</title>\n"
                f"</head>\n"
                f"<body style=\"margin: 0; padding: 0; background-color: #f3f4f6; "
                f"font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; "
                f"-webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;\">\n"
                f"    <table border=\"0\" cellpadding=\"0\" cellspacing=\"0\" width=\"100%\" "
                f"style=\"background-color: #f3f4f6; padding: 20px 0;\">\n"
                f"        <tr>\n"
                f"            <td align=\"center\">\n"
                f"                <table border=\"0\" cellpadding=\"0\" cellspacing=\"0\" width=\"600\" "
                f"style=\"background-color: #ffffff; border-radius: 12px; "
                f"box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); "
                f"overflow: hidden;\">\n"
                f"                    <!-- Brand Header -->\n"
                f"                    <tr>\n"
                f"                        <td align=\"center\" style=\"background: linear-gradient(135deg, "
                f"{self._theme_color}, #312e81); padding: 40px 20px; color: #ffffff;\">\n"
                f"                            <h1 style=\"margin: 0; font-size: 26px; font-weight: 700; "
                f"letter-spacing: -0.5px;\">{html.escape(message_copy.subject)}</h1>\n"
                f"                        </td>\n"
                f"                    </tr>\n"
                f"                    <!-- Content Body -->\n"
                f"                    <tr>\n"
                f"                        <td style=\"padding: 40px 30px; color: #374151; "
                f"font-size: 16px; line-height: 1.6;\">\n"
                f"                            <p style=\"margin: 0;\">{escaped_body}</p>\n"
                f"                        </td>\n"
                f"                    </tr>\n"
                f"                    <!-- Decorative separator -->\n"
                f"                    <tr>\n"
                f"                        <td style=\"padding: 0 30px;\">\n"
                f"                            <div style=\"border-top: 1px solid #e5e7eb;\"></div>\n"
                f"                        </td>\n"
                f"                    </tr>\n"
                f"                    <!-- Footer -->\n"
                f"                    <tr>\n"
                f"                        <td style=\"padding: 30px; text-align: center; font-size: 12px; color: #9ca3af;\">\n"
                f"                            <p style=\"margin: 0 0 8px 0;\">Este es un correo seguro generado "
                f"automáticamente por {self._company_name}.</p>\n"
                f"                            <p style=\"margin: 0;\">&copy; {current_year} {self._company_name}. "
                f"Todos los derechos reservados.</p>\n"
                f"                        </td>\n"
                f"                    </tr>\n"
                f"                </table>\n"
                f"            </td>\n"
                f"        </tr>\n"
                f"    </table>\n"
                f"</body>\n"
                f"</html>\n"
            )

            # Update body and flag
            message_copy.body = html_body
            message_copy.is_html = True

        return super().send(message_copy)
