import json
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.services.auth_service import AuthService, TokenInvalidoError, TokenVerificationError

logger = logging.getLogger(__name__)

# Rutas que no requieren autenticación
RUTAS_PUBLICAS = {"/health", "/docs", "/openapi.json", "/redoc"}


class TokenAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Excluir rutas públicas sin tocar el token
        if request.url.path in RUTAS_PUBLICAS:
            return await call_next(request)

        token = request.query_params.get("token")

        try:
            AuthService.validar_access_token_google(token)
        except TokenInvalidoError as e:
            logger.warning(f"Acceso denegado [{request.url.path}]: {str(e)}")
            return Response(
                content=json.dumps({"detail": "Acceso denegado: Token inválido o expirado."}),
                status_code=401,
                media_type="application/json"
            )
        except TokenVerificationError as e:
            logger.error(f"Error de verificación [{request.url.path}]: {str(e)}")
            return Response(
                content=json.dumps({"detail": "Error interno al validar la identidad."}),
                status_code=500,
                media_type="application/json"
            )

        return await call_next(request)