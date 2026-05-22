"""Main script demonstrating the Email Sender with the Decorator Pattern.

Sends a single notification email that exercises every decorator in one pipeline:
logging, retries, BCC, signature, and HTML template.
"""

import datetime

import config
from src.decorators.bcc_decorator import BccDecorator
from src.decorators.html_decorator import HtmlWrapperDecorator
from src.decorators.logging_decorator import LoggingDecorator
from src.decorators.retry_decorator import RetryDecorator
from src.decorators.signature_decorator import SignatureDecorator
from src.models import EmailMessage
from src.sender.base import BaseEmailSender


def build_notification_pipeline() -> BccDecorator:
    """Build the full decorator chain for a production-style notification."""
    base_sender = BaseEmailSender()

    # Bcc outermost so LoggingDecorator can audit hidden copies.
    # Inner → outer: Base → Html → Signature → Retry → Logging → Bcc
    return BccDecorator(
        LoggingDecorator(
            RetryDecorator(
                SignatureDecorator(
                    HtmlWrapperDecorator(
                        base_sender,
                        theme_color="#4f46e5",
                        company_name="Taller Correo — Patrón Decorator",
                    ),
                    signature=(
                        "Dana Sofía Sánchez\n"
                        "Ingeniería de Software — Universidad de La Salle\n"
                        "Sistema de notificaciones · tallerCorreo v1.0.0"
                    ),
                ),
                retries=2,
                delay=0.1,
            )
        ),
        bcc_recipients=[config.BCC_RECIPIENT],
    )


def main() -> None:
    """Send one definitive notification email using all decorators."""
    recipient_email = "raranda@unisalle.edu.co"
    sender_email = "taller.correo.decorator@gmail.com"
    issued_at = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    print("\n" + "=" * 80)
    print(" SISTEMA DE NOTIFICACIONES — ENVÍO ÚNICO CON PATRÓN DECORATOR ".center(78))
    print("=" * 80)
    print(
        "\nPipeline activo: Bcc → Logging → Retry → Signature → HtmlWrapper → Base\n"
        f"Destinatario visible (To): {recipient_email}\n"
        f"Copia oculta (Bcc):       {config.BCC_RECIPIENT}\n"
    )

    sender = build_notification_pipeline()

    notification = EmailMessage(
        sender=sender_email,
        recipient=recipient_email,
        subject="Notificación del sistema — Taller Patrón Decorator",
        body=(
            f"Estimado/a,\n\n"
            f"El sistema de envío de correos ha generado esta notificación unificada "
            f"el {issued_at}.\n\n"
            f"En un solo mensaje se demuestran todas las capacidades del patrón Decorator:\n\n"
            f"• Plantilla HTML responsiva con diseño profesional\n"
            f"• Firma corporativa insertada automáticamente\n"
            f"• Copia oculta (BCC) hacia el buzón de auditoría\n"
            f"• Registro de actividad en consola y en logs/email_system.log\n"
            f"• Reintentos automáticos ante fallos transitorios de red\n\n"
            f"No es necesario realizar ninguna acción. Este correo confirma que "
            f"el taller de correo electrónico está operativo y listo para revisión."
        ),
    )

    success = sender.send(notification)

    print("\n" + "=" * 80)
    if success:
        print(
            " NOTIFICACIÓN ENVIADA CORRECTAMENTE ".center(78) + "\n"
            "Revisa la carpeta 'output/' para el HTML generado y 'logs/' para la auditoría."
        )
    else:
        print(" EL ENVÍO FINALIZÓ CON ERRORES — REVISA LOS LOGS ".center(78))
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
