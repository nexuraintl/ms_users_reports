from sqlalchemy import create_engine
import os

# Configuración de la BD de Administración (Configuración) desde variables de entorno
DB_CONFIG_URL = f"mysql+pymysql://{os.getenv('DB1_USER')}:{os.getenv('DB1_PASS')}@{os.getenv('DB1_HOST')}/{os.getenv('DB1_NAME')}"
admin_engine = create_engine(DB_CONFIG_URL)

def get_client_engine(creds: dict):
    """
    Crea un motor de base de datos dinámico para el cliente.
    creds: dict con user, pass, host, name
    """
    url = f"mysql+pymysql://{creds['user']}:{creds['pass']}@{creds['host']}:{creds['port']}/{creds['db_name']}"
    return create_engine(url)