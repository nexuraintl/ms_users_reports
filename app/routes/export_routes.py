import logging
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from app.services.config_service import get_db_credentials
from app.services.excel_service import generate_users_report

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/export-users")
def export_users(client_id: str = Query(...)):
    # --- Paso 1: Obtener credenciales desde BD1 ---
    try:
        creds = get_db_credentials(client_id)
    except Exception as e:
        # Fallo de infraestructura: BD1 caída, timeout, error de red, etc.
        logger.error(f"Error accediendo a BD1 para client_id={client_id}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Servicio temporalmente no disponible. No se pudo acceder a la configuración."
        )

    # El cliente no existe en la tabla — no es un error de infraestructura
    if creds is None:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró configuración para el cliente '{client_id}'."
        )

    # --- Paso 2: Generar reporte desde BD2 ---
    try:
        excel_file = generate_users_report(creds)
    except ValueError as e:
        # Problema de esquema: columnas faltantes en tn_user_lst
        logger.error(f"Error de esquema en BD del cliente '{client_id}': {str(e)}")
        raise HTTPException(
            status_code=422,
            detail=f"La base de datos del cliente tiene un esquema inesperado: {str(e)}"
        )
    except Exception as e:
        # Fallo de conexión o consulta a BD2
        logger.error(f"Error generando reporte para client_id={client_id}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="No se pudo generar el reporte. Error al conectar con la base de datos del cliente."
        )

    # --- Paso 3: Retornar archivo ---
    filename = f"reporte_usuarios_{client_id}.xlsx"
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )