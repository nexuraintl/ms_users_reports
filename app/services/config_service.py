from sqlalchemy import text
from app.models.db_config import admin_engine
import logging

logger = logging.getLogger(__name__)

def get_db_credentials(client_id: str):
    """
    Consulta en la tabla tn_gestion_bdconex las credenciales 
    específicas para el ID del cliente proporcionado.
    """
    # Usamos los nombres exactos de tu estructura
    query = text("""
        SELECT 
            usuario, 
            contrasena, 
            hosting, 
            nombreBaseDeDatos,
            puerto 
        FROM tn_gestion_bdconex 
        WHERE idCliente = :cid 
        LIMIT 1
    """)
    
    try:
        with admin_engine.connect() as conn:
            # Importante: Asegúrate de que la conexión inicial de admin_engine 
            # apunte a la base de datos 'pre_gestion_bdconex'
            result = conn.execute(query, {"cid": client_id}).mappings().first()
            
        if not result:
            logger.warning(f"⚠️ No se encontraron credenciales para el cliente: {client_id}")
            return None
        
        # Mapeamos a un diccionario estándar para el motor dinámico
        return {
            "user": result['usuario'],
            "pass": result['contrasena'],
            "host": result['hosting'],
            "db_name": result['nombreBaseDeDatos'],
            "port": result['puerto'] or 3306 # Default MySQL port
        }
    except Exception as e:
        logger.error(f"🔥 Error consultando la tabla de gestión: {str(e)}")
        return None