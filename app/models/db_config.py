from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import os
import logging

logger = logging.getLogger(__name__)

# Engine de BD1 — se inicializa lazy en el primer uso, no en tiempo de import
_admin_engine: Engine | None = None


def get_admin_engine() -> Engine:
    global _admin_engine
    if _admin_engine is None:
        required = ["DB1_USER", "DB1_PASS", "DB1_HOST", "DB1_NAME"]
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            raise RuntimeError(f"Variables de entorno faltantes para BD1: {missing}")

        url = (
            f"mysql+pymysql://{os.getenv('DB1_USER')}:{os.getenv('DB1_PASS')}"
            f"@{os.getenv('DB1_HOST')}/{os.getenv('DB1_NAME')}"
        )
        _admin_engine = create_engine(
            url,
            pool_size=2,
            max_overflow=3,
            pool_timeout=10,
            pool_recycle=1800,
        )
        logger.info("Admin engine inicializado.")
    return _admin_engine


def get_client_engine(creds: dict) -> Engine:
    """
    Crea un engine desechable para la BD del cliente.
    Diseñado para usarse con context manager y dispose() explícito tras cada uso.
    pool_size=1 + max_overflow=0: abre exactamente una conexión y la cierra.
    """
    url = (
        f"mysql+pymysql://{creds['user']}:{creds['pass']}"
        f"@{creds['host']}:{creds['port']}/{creds['db_name']}"
    )
    return create_engine(
        url,
        pool_size=1,
        max_overflow=0,
        pool_timeout=10,
        pool_recycle=1800,
    )