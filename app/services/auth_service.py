from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

class AuthService:
    _request_adapter = requests.Request()
    # Tu Audience específica
    EXPECTED_AUDIENCE = "618104708054-9r9s1c4alg36erliucho9t52n32n6dgq.apps.googleusercontent.com"

    @staticmethod
    def validar_access_token_google(token: str):
        try:
            # Validación criptográfica contra los certs de Google
            id_info = id_token.verify_oauth2_token(
                token, 
                AuthService._request_adapter, 
                AuthService.EXPECTED_AUDIENCE
            )
            logger.info(f"🔐 Token verificado para: {id_info.get('email')}")
            return id_info

        except ValueError as e:
            logger.error(f"❌ Fallo de seguridad en JWT: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Acceso denegado: Token de seguridad inválido o expirado."
            )
        except Exception as e:
            logger.error(f"🔥 Error inesperado validando identidad: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al validar la identidad del solicitante."
            )