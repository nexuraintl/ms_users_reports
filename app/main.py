from fastapi import FastAPI
from app.middleware import TokenAuthMiddleware
from app.routes import export_routes

app = FastAPI(title="MS Users Report")

# Registro del Middleware de seguridad (API Gateway Logic)
app.add_middleware(TokenAuthMiddleware)

# Inclusión de rutas
app.include_router(export_routes.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "healthy"}