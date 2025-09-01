# app/schemas/blacklist.py
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class BlacklistReasonStats(BaseModel):
    """Estadísticas por razón de invalidación"""
    reason: str = Field(..., description="Razón de invalidación")
    count: int = Field(..., description="Cantidad de tokens con esta razón")


class BlacklistStats(BaseModel):
    """Estadísticas generales de la blacklist"""
    total_blacklisted_tokens: int = Field(..., description="Total de tokens en blacklist")
    recent_blacklisted_24h: int = Field(..., description="Tokens invalidados en las últimas 24 horas")
    blacklist_reasons: List[BlacklistReasonStats] = Field(..., description="Estadísticas por razón")
    generated_at: str = Field(..., description="Timestamp de generación del reporte")
    error: Optional[str] = Field(None, description="Error si hubo problemas generando stats")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_blacklisted_tokens": 157,
                "recent_blacklisted_24h": 23,
                "blacklist_reasons": [
                    {"reason": "logout", "count": 134},
                    {"reason": "admin_action", "count": 15},
                    {"reason": "security_logout", "count": 8}
                ],
                "generated_at": "2024-09-03T15:30:00",
                "error": None
            }
        }
    }


class BlacklistCleanupResponse(BaseModel):
    """Respuesta de limpieza de blacklist"""
    message: str = Field(..., description="Mensaje de confirmación")
    tokens_cleaned: int = Field(..., description="Cantidad de tokens eliminados")
    days_threshold: int = Field(..., description="Umbral de días usado para la limpieza")
    cleanup_date: str = Field(..., description="Fecha y hora de la limpieza")

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Limpieza completada exitosamente",
                "tokens_cleaned": 45,
                "days_threshold": 30,
                "cleanup_date": "2024-09-03T15:35:00"
            }
        }
    }


class ForceLogoutResponse(BaseModel):
    """Respuesta de logout forzado por admin"""
    message: str = Field(..., description="Mensaje de confirmación")
    user_id: int = Field(..., description="ID del usuario afectado")
    sessions_closed: int = Field(..., description="Cantidad de sesiones cerradas")
    reason: str = Field(..., description="Razón del logout forzado")
    admin_user: str = Field(..., description="Nombre del administrador que ejecutó la acción")

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Logout forzado aplicado al usuario Juan Pérez",
                "user_id": 5,
                "sessions_closed": 3,
                "reason": "security_breach",
                "admin_user": "Admin Cinema"
            }
        }
    }


class TokenBlacklistResponse(BaseModel):
    """Información de un token en blacklist"""
    id: int = Field(..., description="ID del registro")
    user_id: int = Field(..., description="ID del usuario")
    user_email: str = Field(..., description="Email del usuario")
    reason: str = Field(..., description="Razón de invalidación")
    blacklisted_at: datetime = Field(..., description="Fecha y hora de invalidación")

    @classmethod
    def from_orm(cls, blacklist_record):
        """Crear respuesta desde el modelo TokenBlacklist"""
        return cls(
            id=blacklist_record.id,
            user_id=blacklist_record.user_id,
            user_email=blacklist_record.user_email,
            reason=blacklist_record.reason,
            blacklisted_at=blacklist_record.blacklisted_at
        )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 123,
                "user_id": 5,
                "user_email": "juan.perez@gmail.com",
                "reason": "logout",
                "blacklisted_at": "2024-09-03T14:30:00"
            }
        }
    }


class BlacklistListResponse(BaseModel):
    """Lista paginada de tokens en blacklist"""
    tokens: List[TokenBlacklistResponse] = Field(..., description="Lista de tokens blacklisted")
    total_count: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Tamaño de página")
    total_pages: int = Field(..., description="Total de páginas")

    model_config = {
        "json_schema_extra": {
            "example": {
                "tokens": [
                    {
                        "id": 123,
                        "user_id": 5,
                        "user_email": "juan.perez@gmail.com",
                        "reason": "logout",
                        "blacklisted_at": "2024-09-03T14:30:00"
                    }
                ],
                "total_count": 157,
                "page": 1,
                "page_size": 20,
                "total_pages": 8
            }
        }
    }
