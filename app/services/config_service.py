from sqlalchemy import text
from app.models.db_config import get_admin_engine
import logging

logger = logging.getLogger(__name__)


def get_db_credentials(client_id: str) -> dict | None:
    """
    Consulta en tn_gestion_bdconex las credenciales del cliente indicado.
    Retorna None si el cliente no existe. Lanza excepción si hay fallo de infraestructura.
    """
    query = text("""
        SELECT usuario, contrasena, hosting, nombreBaseDeDatos, puerto
        FROM tn_gestion_bdconex
        WHERE idCliente = :cid
        LIMIT 1
    """)

    with get_admin_engine().connect() as conn:
        result = conn.execute(query, {"cid": client_id}).mappings().first()

    if not result:
        logger.warning(f"No se encontraron credenciales para client_id: {client_id}")
        return None

    return {
        "user":    result["usuario"],
        "pass":    result["contrasena"],
        "host":    result["hosting"],
        "db_name": result["nombreBaseDeDatos"],
        "port":    result["puerto"] or 3306,
    }