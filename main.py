"""Main script demonstrating the Email Sender with the Decorator Pattern.

This script constructs various pipelines of decorators to show the power,
flexibility, and compliance with SOLID, PEP 8, and Clean Code.
It targets sending to dsofia0528@gmail.com.
"""

from src.models import EmailMessage
from src.sender.base import BaseEmailSender
from src.decorators.logging_decorator import LoggingDecorator
from src.decorators.signature_decorator import SignatureDecorator
from src.decorators.html_decorator import HtmlWrapperDecorator
from src.decorators.retry_decorator import RetryDecorator


def print_header(title: str) -> None:
    """Helper function to print sections in a beautiful format."""
    print("\n" + "=" * 80)
    print(f" {title.center(78)} ")
    print("=" * 80)


def main() -> None:
    """Execute three email sending scenarios using different decorator pipelines."""
    # Common destination email as requested
    recipient_email = "dsofia0528@gmail.com"
    sender_email = "taller.correo.decorator@gmail.com"

    # -------------------------------------------------------------------------
    # CASO 1: Envío Básico
    # -------------------------------------------------------------------------
    print_header("CASO 1: ENVÍO BÁSICO (Componente Concreto)")
    print("Descripción: Envío simple de texto plano sin ningún decorador adicional.\n")

    base_sender = BaseEmailSender()

    msg_1 = EmailMessage(
        sender=sender_email,
        recipient=recipient_email,
        subject="Caso 1: Correo Básico",
        body="Este es un correo básico en texto plano, sin formato ni logs adicionales."
    )

    base_sender.send(msg_1)

    # -------------------------------------------------------------------------
    # CASO 2: Envío Auditado con Firma Corporativa
    # -------------------------------------------------------------------------
    print_header("CASO 2: ENVÍO AUDITADO CON FIRMA (Logs + Firma + Base)")
    print("Descripción: Añade logs automáticos del envío y una firma al final.\n")

    # Chaining decorators: LoggingDecorator -> SignatureDecorator -> BaseEmailSender
    sender_case_2 = LoggingDecorator(
        SignatureDecorator(
            base_sender,
            signature="Atentamente,\nEquipo de Ingeniería de Software\nUniversidad de La Salle"
        )
    )

    msg_2 = EmailMessage(
        sender=sender_email,
        recipient=recipient_email,
        subject="Caso 2: Correo con Firma y Auditoría",
        body=(
            "Estimada Sofía,\n\n"
            "Este correo incluye logs en consola/archivo y una firma automática en el pie de página."
        )
    )

    sender_case_2.send(msg_2)

    # -------------------------------------------------------------------------
    # CASO 3: Envío Premium Completo
    # -------------------------------------------------------------------------
    print_header("CASO 3: ENVÍO PREMIUM COMPLETO (Logs + Retry + Firma + HTML + Base)")
    print(
        "Descripción: Transforma el texto plano en una plantilla HTML premium, "
        "añade firma formateada, ofrece tolerancia a fallos mediante reintentos, "
        "y registra todas las métricas en archivos de logs.\n"
    )

    # Chaining decorators: Logging -> Retry -> Signature -> HtmlWrapper -> Base
    sender_case_3 = LoggingDecorator(
        RetryDecorator(
            SignatureDecorator(
                HtmlWrapperDecorator(
                    base_sender,
                    theme_color="#4f46e5",  # Modern Indigo
                    company_name="Taller Decorador S.A.S."
                ),
                signature="Sofía Sánchez\nLíder de Desarrollo Académico\nContacto: dsofia0528@gmail.com"
            ),
            retries=2,
            delay=0.1
        )
    )

    msg_3 = EmailMessage(
        sender=sender_email,
        recipient=recipient_email,
        subject="Caso 3: Experiencia Premium Completa",
        body=(
            "Hola Sofia,\n\n"
            "Este es un mensaje redactado en texto plano que ha sido interceptado "
            "y decorado dinámicamente con una plantilla HTML profesional, responsiva y estética.\n\n"
            "Además, el sistema es tolerante a fallos de red gracias a la política "
            "de reintentos automáticos configurada a nivel estructural."
        )
    )

    sender_case_3.send(msg_3)

    print_header("DEMOSTRACIÓN FINALIZADA CON ÉXITO")
    print(
        "Todos los correos han sido simulados y guardados de forma segura en la carpeta 'output/'\n"
        "y los logs en la carpeta 'logs/'. ¡Por favor, revisa estos directorios para observar los resultados!"
    )
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
