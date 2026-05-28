import io
import logging

import pandas as pd
from sqlalchemy import text

from app.models.db_config import get_client_engine

logger = logging.getLogger(__name__)

# Ajustar a "s" si se confirma que date_ct almacena epoch en segundos
DATE_CT_UNIT = "s"

# Zona horaria del cliente — Colombia no aplica DST, es fija UTC-5
CLIENT_TIMEZONE = "America/Bogota"

# Límite de caracteres por celda en Excel (hard limit de la especificación OOXML)
EXCEL_CELL_CHAR_LIMIT = 32_767

COLUMNS_TO_SELECT = [
    "id",
    "date_ct",
    "ip",
    "user_id",
    "login",
    "tn_table",
    "tn_table_2",
    "id_primary_table",
    "action",
    "info",
]

COLUMN_MAPPING = {
    "id":               "ID Registro",
    "date_ct":          "Fecha",
    "ip":               "IP",
    "user_id":          "ID Usuario",
    "login":            "Login",
    "tn_table":         "Tabla",
    "tn_table_2":       "Tabla secundaria",
    "id_primary_table": "ID Registro afectado",
    "action":           "Acción",
    "info":             "Detalle",
}


def generate_audit_report(
    creds: dict,
    fecha_inicio: int,
    fecha_fin: int,
) -> io.BytesIO:
    """
    Descarga registros de tn_sx_log en el rango [fecha_inicio, fecha_fin]
    y los exporta a un archivo .xlsx.

    Parámetros
    ----------
    creds        : credenciales de conexión a la BD del cliente
    fecha_inicio : epoch en ms (inclusive)
    fecha_fin    : epoch en ms (inclusive)
    """
    engine = get_client_engine(creds)

    try:
        cols_sql = ", ".join(COLUMNS_TO_SELECT)
        query = text(
            f"SELECT {cols_sql} FROM tn_sx_log "
            f"WHERE date_ct >= :fecha_inicio AND date_ct <= :fecha_fin "
            f"ORDER BY date_ct DESC"
        )

        with engine.connect() as conn:
            df = pd.read_sql(
                query,
                conn,
                params={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
            )

    except Exception as e:
        logger.error(
            "Error consultando tn_sx_log para host %s: %s",
            creds.get("host"),
            str(e),
        )
        raise
    finally:
        engine.dispose()

    missing_cols = [c for c in COLUMNS_TO_SELECT if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Columnas faltantes en tn_sx_log: {missing_cols}")

    if not df.empty:
        # Convertir epoch → datetime con zona horaria del cliente, sin tz para Excel
        df["date_ct"] = (
            pd.to_datetime(df["date_ct"], unit=DATE_CT_UNIT, errors="coerce")
            .dt.tz_localize("UTC")
            .dt.tz_convert(CLIENT_TIMEZONE)
            .dt.tz_localize(None)  # openpyxl no soporta datetimes con tz
        )

        # Truncar info si supera el límite de celda de Excel
        if "info" in df.columns:
            mask = df["info"].str.len() > EXCEL_CELL_CHAR_LIMIT
            if mask.any():
                logger.warning(
                    "%d filas tienen 'info' truncada al límite de %d caracteres de Excel.",
                    mask.sum(),
                    EXCEL_CELL_CHAR_LIMIT,
                )
                df.loc[mask, "info"] = (
                    df.loc[mask, "info"].str[:EXCEL_CELL_CHAR_LIMIT - 3] + "..."
                )

    df_final = df.rename(columns=COLUMN_MAPPING)[list(COLUMN_MAPPING.values())]

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_final.to_excel(writer, index=False, sheet_name="Auditoría")

    output.seek(0)
    return output