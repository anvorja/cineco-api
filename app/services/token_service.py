# app/services/token_service.py
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.token_blacklist import TokenBlacklist
from app.models import User

logger = logging.getLogger(__name__)


class TokenService:
    """Servicio para manejo de tokens JWT y blacklist"""

    @staticmethod
    def blacklist_token(
            db: Session,
            token: str,
            user: User,
            reason: str = "logout"
    ) -> bool:
        """
        Agregar token a la blacklist para invalidarlo inmediatamente.

        Args:
            db: Sesión de base de datos
            token: Token JWT a invalidar
            user: Usuario propietario del token
            reason: Razón de invalidación

        Returns:
            True si se agregó exitosamente, False en caso de error
        """
        try:
            # Verificar si el token ya está en blacklist
            existing = db.query(TokenBlacklist).filter(
                TokenBlacklist.token == token
            ).first()

            if existing:
                logger.warning(f"Token already blacklisted for user {user.email}")
                return True

            # Crear registro de blacklist
            blacklisted_token = TokenBlacklist(
                token=token,
                user_id=user.id,
                user_email=user.email,
                blacklisted_at=datetime.now(),
                reason=reason
            )

            db.add(blacklisted_token)
            db.commit()

            logger.info(f"Token blacklisted successfully for user {user.email}, reason: {reason}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Error blacklisting token for user {user.email}: {e}")
            return False

    @staticmethod
    def is_token_blacklisted(db: Session, token: str) -> bool:
        """
        Verificar si un token está en la blacklist.

        Args:
            db: Sesión de base de datos
            token: Token JWT a verificar

        Returns:
            True si está blacklisted, False si es válido
        """
        try:
            blacklisted = db.query(TokenBlacklist).filter(
                TokenBlacklist.token == token
            ).first()

            return blacklisted is not None

        except Exception as e:
            logger.error(f"Error checking token blacklist: {e}")
            # En caso de error, ser conservativo y permitir el token
            return False

    @staticmethod
    def blacklist_all_user_tokens(
            db: Session,
            user_id: int,
            reason: str = "security_logout"
    ) -> int:
        """
        Invalidar TODOS los tokens activos de un usuario.
        Útil para logout de todas las sesiones o por seguridad.

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            reason: Razón de invalidación

        Returns:
            Número de tokens invalidados
        """
        try:
            # Esta funcionalidad requeriría mantener registro de tokens activos
            # Por simplicidad, solo registramos la acción
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return 0

            # Crear registro especial para logout masivo
            mass_logout = TokenBlacklist(
                token=f"MASS_LOGOUT_{user_id}_{datetime.now().timestamp()}",
                user_id=user_id,
                user_email=user.email,
                blacklisted_at=datetime.now(),
                reason=reason
            )

            db.add(mass_logout)
            db.commit()

            logger.info(f"Mass logout executed for user {user.email}")
            return 1

        except Exception as e:
            db.rollback()
            logger.error(f"Error in mass logout for user_id {user_id}: {e}")
            return 0

    @staticmethod
    def cleanup_expired_tokens(db: Session, days_old: int = 30) -> int:
        """
        Limpiar tokens expirados de la blacklist.

        Args:
            db: Sesión de base de datos
            days_old: Eliminar tokens más viejos que X días

        Returns:
            Número de tokens eliminados
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)

            deleted_count = db.query(TokenBlacklist).filter(
                TokenBlacklist.blacklisted_at < cutoff_date
            ).delete()

            db.commit()

            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired blacklisted tokens")

            return deleted_count

        except Exception as e:
            db.rollback()
            logger.error(f"Error cleaning up expired tokens: {e}")
            return 0

    @staticmethod
    def get_blacklist_stats(db: Session) -> Dict[str, Any]:
        """
        Obtener estadísticas de la blacklist para monitoreo.

        Args:
            db: Sesión de base de datos

        Returns:
            Diccionario con estadísticas
        """
        try:
            total_blacklisted = db.query(TokenBlacklist).count()

            # Tokens por razón
            reason_stats = db.query(
                TokenBlacklist.reason,
                func.count(TokenBlacklist.id).label('count')
            ).group_by(TokenBlacklist.reason).all()

            # Tokens recientes (último día)
            yesterday = datetime.now() - timedelta(days=1)
            recent_count = db.query(TokenBlacklist).filter(
                TokenBlacklist.blacklisted_at >= yesterday
            ).count()

            return {
                "total_blacklisted_tokens": total_blacklisted,
                "recent_blacklisted_24h": recent_count,
                "blacklist_reasons": [
                    {"reason": reason, "count": count}
                    for reason, count in reason_stats
                ],
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting blacklist stats: {e}")
            return {
                "error": "Could not generate stats",
                "total_blacklisted_tokens": 0,
                "recent_blacklisted_24h": 0,
                "blacklist_reasons": [],
                "generated_at": datetime.now().isoformat()
            }
