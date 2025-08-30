# app/services/email_service.py
import logging
from typing import List

from app.models import User, Purchase, Ticket
from app.utils.helpers import format_currency

logger = logging.getLogger(__name__)


class EmailService:
    """Service for email operations (simulated for MVP)"""

    @staticmethod
    async def send_purchase_confirmation(user: User, purchase: Purchase, tickets: List[Ticket]) -> bool:
        """
        Send purchase confirmation email (simulated).
        In production, this would integrate with SendGrid or similar service.

        Args:
            user: User who made the purchase
            purchase: Purchase object
            tickets: List of ticket objects

        Returns:
            True if email sent successfully (always True in simulation)
        """
        try:
            # Generate email content
            email_content = EmailService._generate_confirmation_email(user, purchase, tickets)

            # Log the email instead of actually sending it (MVP simulation)
            logger.info("=" * 50)
            logger.info("SIMULATED EMAIL SENT")
            logger.info("=" * 50)
            logger.info(f"To: {user.email}")
            logger.info(f"Subject: Confirmación de Compra - Cinema Tickets")
            logger.info("-" * 50)
            logger.info(email_content)
            logger.info("=" * 50)

            return True

        except Exception as e:
            logger.error(f"Error sending confirmation email: {e}")
            return False

    @staticmethod
    def _generate_confirmation_email(user: User, purchase: Purchase, tickets: List[Ticket]) -> str:
        """
        Generate confirmation email content.

        Args:
            user: User object
            purchase: Purchase object
            tickets: List of ticket objects

        Returns:
            Email content as string
        """
        movie_title = purchase.movie.title if purchase.movie else "Unknown Movie"

        email_content = f"""
¡Hola {user.full_name}!

Tu compra de entradas de cine ha sido confirmada exitosamente.

DETALLES DE LA COMPRA:
========================
Número de Compra: #{purchase.id}
Película: {movie_title}
Fecha de Compra: {purchase.created_at.strftime('%d/%m/%Y %H:%M')}
Cantidad de Entradas: {purchase.quantity}
Precio Total: {format_currency(purchase.total_amount)}
Estado: {purchase.status.value.upper()}

INFORMACIÓN DE TUS ENTRADAS:
===========================
"""

        for ticket in tickets:
            email_content += f"""
- Código de Entrada: {ticket.ticket_code}
  Asiento: {ticket.seat_number}
  Estado: {ticket.status.value.upper()}
"""

        email_content += f"""

INFORMACIÓN DE PAGO:
===================
Tarjeta: **** **** **** {purchase.payment_info.get('last_four', '****')}
Transacción: {purchase.payment_info.get('transaction_id', 'N/A')}

INSTRUCCIONES:
=============
1. Presenta tus códigos de entrada en la taquilla del cine
2. Los códigos son únicos y no transferibles
3. Conserva este email como comprobante de compra

¡Disfruta la película!

Cinema Ticket API
support@cinema.com
"""

        return email_content.strip()

    @staticmethod
    async def send_welcome_email(user: User) -> bool:
        """
        Send welcome email to new users (simulated).

        Args:
            user: New user object

        Returns:
            True if email sent successfully
        """
        try:
            welcome_content = f"""
¡Bienvenido a Cinema Ticket API, {user.full_name}!

Tu cuenta ha sido creada exitosamente.

DETALLES DE TU CUENTA:
=====================
Email: {user.email}
Nombre: {user.full_name}
Teléfono: {user.phone}
Fecha de Registro: {user.created_at.strftime('%d/%m/%Y %H:%M')}

Ahora puedes:
- Explorar nuestra cartelera de películas
- Comprar entradas para tus películas favoritas  
- Ver tu historial de compras

¡Gracias por unirte a nosotros!

Cinema Ticket API
support@cinema.com
"""

            logger.info("=" * 50)
            logger.info("SIMULATED WELCOME EMAIL SENT")
            logger.info("=" * 50)
            logger.info(f"To: {user.email}")
            logger.info(f"Subject: Bienvenido a Cinema Ticket API")
            logger.info("-" * 50)
            logger.info(welcome_content.strip())
            logger.info("=" * 50)

            return True

        except Exception as e:
            logger.error(f"Error sending welcome email: {e}")
            return False