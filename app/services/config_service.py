from sqlalchemy import text
from app.models.db_config import admin_engine

def get_db_credentials(client_id: str):
    query = text("SELECT db_user, db_pass, db_host, db_name FROM clientes_config WHERE client_id = :cid")
    
    with admin_engine.connect() as conn:
        result = conn.execute(query, {"cid": client_id}).mappings().first()
        
    if not result:
        return None
    
    return {
        "user": result['db_user'],
        "pass": result['db_pass'],
        "host": result['db_host'],
        "db_name": result['db_name']
    }