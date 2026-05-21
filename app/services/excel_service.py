import pandas as pd
import io
import logging
from sqlalchemy import text
from app.models.db_config import get_client_engine

logger = logging.getLogger(__name__)

# Columnas que se extraen explícitamente — sin SELECT *
COLUMNS_TO_SELECT = [
    "id", "nombre", "login", "tipo_doc", "identificacion",
    "email", "direccion", "telefono", "pais", "departamento",
    "ciudad", "tipo", "estado", "tipo_wf",
]

COLUMN_MAPPING = {
    "id":             "ID Registro",
    "nombre":         "Nombre",
    "login":          "Login",
    "tipo_doc":       "Tipo de identificación",
    "identificacion": "Número de identificación",
    "email":          "E-mail",
    "direccion":      "Dirección",
    "telefono":       "Teléfono",
    "pais":           "País",
    "departamento":   "Departamento",
    "ciudad":         "Municipio",
    "tipo":           "Tipo",
    "estado":         "Estado",
    "tipo_wf":        "Tipo de registro",
}


def generate_users_report(creds: dict) -> io.BytesIO:
    engine = get_client_engine(creds)

    try:
        cols_sql = ", ".join(COLUMNS_TO_SELECT)
        query = text(f"SELECT {cols_sql} FROM tn_user_lst")

        with engine.connect() as conn:
            df = pd.read_sql(query, conn)

    except Exception as e:
        logger.error(f"Error consultando tn_user_lst para host {creds.get('host')}: {str(e)}")
        raise
    finally:
        # Garantiza cierre de conexiones independientemente del resultado
        engine.dispose()

    # Validar que las columnas esperadas estén presentes antes de renombrar
    missing_cols = [c for c in COLUMNS_TO_SELECT if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Columnas faltantes en tn_user_lst: {missing_cols}")

    df_final = df.rename(columns=COLUMN_MAPPING)[list(COLUMN_MAPPING.values())]

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_final.to_excel(writer, index=False, sheet_name="Usuarios")

    output.seek(0)
    return output