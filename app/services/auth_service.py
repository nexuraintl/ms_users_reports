from google.oauth2 import id_token
from google.auth.transport import requests
import logging

logger = logging.getLogger(__name__)


class TokenInvalidoError(Exception):
    """Token ausente, con firma inválida o expirado."""
    pass


class TokenVerificationError(Exception):
    """Error inesperado durante la verificación (problema de infraestructura)."""
    pass


class AuthService:
    _request_adapter = requests.Request()
    EXPECTED_AUDIENCE = "618104708054-9r9s1c4alg36erliucho9t52n32n6dgq.apps.googleusercontent.com"

    @staticmethod
    def validar_access_token_google(token: str) -> dict:
        if not token:
            raise TokenInvalidoError("Token ausente en la petición.")

        try:
            id_info = id_token.verify_oauth2_token(
                token,
                AuthService._request_adapter,
                AuthService.EXPECTED_AUDIENCE
            )
            logger.info(f"Token verificado para: {id_info.get('email')}")
            return id_info

        except ValueError as e:
            # Firma inválida, token expirado, audience incorrecta
            logger.warning(f"Token inválido: {str(e)}")
            raise TokenInvalidoError("Token de seguridad inválido o expirado.")

        except Exception as e:
            # Error de red al buscar certs de Google u otro fallo inesperado
            logger.error(f"Error inesperado validando token: {str(e)}")
            raise TokenVerificationError("Error interno al validar la identidad.")