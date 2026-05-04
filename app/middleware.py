from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.auth_service import AuthService

class TokenAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Extraer parámetros de la URL
        token = request.query_params.get("token")
        
        # 2. Validar token usando la lógica de Google
        # Si falla, el método lanza HTTPException (401 o 500)
        AuthService.validar_access_token_google(token)

        # 3. Continuar si es válido
        response = await call_next(request)
        return response