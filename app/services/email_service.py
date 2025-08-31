# app/services/email_service.py
import os
import logging
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import List, Dict, Any

from app.models import User, Purchase, Ticket
from app.utils.helpers import format_currency
from app.core.config import settings

logger = logging.getLogger(__name__)

# Email configuration
EMAIL_CONFIG = {
    'host': settings.EMAIL_HOST,
    'port': settings.EMAIL_PORT,
    'user': settings.EMAIL_USER,
    'password': settings.EMAIL_APP_PASSWORD,
    'from_email': f'"Cinema Tickets" <{settings.EMAIL_USER}>'
}

# Template environment
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
template_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(['html', 'xml'])
)


class EmailService:
    """Service for email operations with HTML templates"""

    @staticmethod
    async def send_email(subject: str, html_content: str, to_email: str) -> bool:
        """
        Send email using SMTP with HTML content.

        Args:
            subject: Email subject
            html_content: HTML email content
            to_email: Recipient email address

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # For MVP, if email credentials are not configured, just log
            if not EMAIL_CONFIG['user'] or not EMAIL_CONFIG['password']:
                logger.info("=" * 60)
                logger.info("SIMULATED EMAIL SENT (No SMTP configured)")
                logger.info("=" * 60)
                logger.info(f"To: {to_email}")
                logger.info(f"Subject: {subject}")
                logger.info("-" * 60)
                logger.info("HTML content would be sent here...")
                logger.info("=" * 60)
                return True

            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = EMAIL_CONFIG['from_email']
            msg['To'] = to_email
            msg['Subject'] = subject

            # Attach HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)

            # SOLUCIÓN: Usar la configuración correcta según el puerto
            if EMAIL_CONFIG['port'] == 465:
                # Puerto 465: SSL directo
                async with aiosmtplib.SMTP(
                    hostname=EMAIL_CONFIG['host'],
                    port=EMAIL_CONFIG['port'],
                    use_tls=True  # SSL directo para puerto 465
                ) as smtp:
                    await smtp.login(EMAIL_CONFIG['user'], EMAIL_CONFIG['password'])
                    await smtp.send_message(msg)
            else:
                # Puerto 587: STARTTLS
                async with aiosmtplib.SMTP(
                    hostname=EMAIL_CONFIG['host'],
                    port=EMAIL_CONFIG['port']
                ) as smtp:
                    await smtp.starttls()  # Upgrade a TLS para puerto 587
                    await smtp.login(EMAIL_CONFIG['user'], EMAIL_CONFIG['password'])
                    await smtp.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return False

    @staticmethod
    async def send_purchase_confirmation(user: User, purchase: Purchase, tickets: List[Ticket]) -> bool:
        """
        Send purchase confirmation email using HTML template.

        Args:
            user: User who made the purchase
            purchase: Purchase object
            tickets: List of ticket objects

        Returns:
            True if email sent successfully
        """
        try:
            # Prepare template data
            template_data = {
                'customer_name': user.full_name,
                'movie_title': purchase.movie.title,
                'movie_genre': purchase.movie.genre,
                'movie_duration': purchase.movie.duration,
                'movie_rating': purchase.movie.rating,
                'purchase_id': purchase.id,
                'purchase_date': purchase.created_at.strftime('%d/%m/%Y'),
                'purchase_time': purchase.created_at.strftime('%H:%M'),
                'quantity': purchase.quantity,
                'total_amount': format_currency(purchase.total_amount),
                'status': purchase.status.value.upper(),
                'tickets': [
                    {
                        'code': ticket.ticket_code,
                        'seat': ticket.seat_number,
                        'status': ticket.status.value.upper()
                    }
                    for ticket in tickets
                ],
                'payment_last_four': purchase.payment_info.get('last_four', '****') if purchase.payment_info else '****',
                'transaction_id': purchase.payment_info.get('transaction_id', 'N/A') if purchase.payment_info else 'N/A',
                'qr_code_data': f"CINEMA-{purchase.id}-{tickets[0].ticket_code if tickets else 'NOTICKET'}",
                'support_email': 'support@cinema.com'
            }

            # Render template
            template = template_env.get_template('purchase_confirmation.html')
            html_content = template.render(**template_data)

            # Send email
            subject = f"Confirmación de Compra #{purchase.id} - Cinema Tickets"
            return await EmailService.send_email(subject, html_content, user.email)

        except Exception as e:
            logger.error(f"Error sending purchase confirmation email: {e}")
            return False

    @staticmethod
    async def send_welcome_email(user: User) -> bool:
        """
        Send welcome email to new users using HTML template.

        Args:
            user: New user object

        Returns:
            True if email sent successfully
        """
        try:
            # Prepare template data
            template_data = {
                'customer_name': user.full_name,
                'email': user.email,
                'phone': user.phone,
                'registration_date': user.created_at.strftime('%d/%m/%Y'),
                'registration_time': user.created_at.strftime('%H:%M'),
                'support_email': 'support@cinema.com'
            }

            # Render template
            template = template_env.get_template('welcome_email.html')
            html_content = template.render(**template_data)

            # Send email
            subject = "¡Bienvenido a Cinema Tickets!"
            return await EmailService.send_email(subject, html_content, user.email)

        except Exception as e:
            logger.error(f"Error sending welcome email: {e}")
            return False

    @staticmethod
    async def render_and_send_email(data: Dict[str, Any], subject: str, template_name: str, to_email: str) -> bool:
        """
        Generic method to render template and send email.

        Args:
            data: Template data dictionary
            subject: Email subject
            template_name: Template file name
            to_email: Recipient email

        Returns:
            True if email sent successfully
        """
        try:
            template = template_env.get_template(template_name)
            html_content = template.render(**data)
            return await EmailService.send_email(subject, html_content, to_email)
        except Exception as e:
            logger.error(f"Error rendering and sending email: {e}")
            return False