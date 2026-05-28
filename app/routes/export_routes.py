import logging

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse

from app.services.config_service import get_db_credentials
from app.services.excel_service import generate_users_report
from app.services.audit_service import generate_audit_report

logger = logging.getLogger(__name__)

router = APIRouter()

LETRAS_VALIDAS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def _validar_letra(letra: str) -> str:
    letra_upper = letra.strip().upper()

    if letra_upper == "TODOS":
        return "Todos"

    if letra_upper in LETRAS_VALIDAS:
        return letra_upper

    raise HTTPException(
        status_code=422,
        detail=f"Parámetro 'letra' inválido: '{letra}'. Debe ser una letra A-Z o 'Todos'.",
    )


def _get_creds_o_404(client_id: str) -> dict:
    try:
        creds = get_db_credentials(client_id)
    except Exception as e:
        logger.error("Error accediendo a BD1 para client_id=%s: %s", client_id, str(e))
        raise HTTPException(
            status_code=503,
            detail="Servicio temporalmente no disponible. No se pudo acceder a la configuración.",
        )

    if creds is None:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró configuración para el cliente '{client_id}'.",
        )

    return creds


@router.get("/export-users")
def export_users(
    client_id: str = Query(...),
    letra: str = Query(...),
):
    letra_normalizada = _validar_letra(letra)
    creds = _get_creds_o_404(client_id)

    try:
        excel_file = generate_users_report(creds, letra=letra_normalizada)
    except ValueError as e:
        logger.error("Error de esquema en BD del cliente '%s': %s", client_id, str(e))
        raise HTTPException(
            status_code=422,
            detail=f"La base de datos del cliente tiene un esquema inesperado: {str(e)}",
        )
    except Exception as e:
        logger.error("Error generando reporte para client_id=%s: %s", client_id, str(e))
        raise HTTPException(
            status_code=503,
            detail="No se pudo generar el reporte. Error al conectar con la base de datos del cliente.",
        )

    sufijo = letra_normalizada.lower() if letra_normalizada != "Todos" else "todos"
    filename = f"reporte_usuarios_{client_id}_{sufijo}.xlsx"

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/export-audit")
def export_audit(
    client_id: str = Query(..., description="ID del cliente registrado en BD1."),
    fecha_inicio: int = Query(..., description="Timestamp de inicio (inclusive), mismo formato que date_ct en tn_sx_log."),
    fecha_fin: int = Query(..., description="Timestamp de fin (inclusive), mismo formato que date_ct en tn_sx_log."),
):
    """
    Descarga el log de auditoría (tn_sx_log) de la BD del cliente
    en el rango [fecha_inicio, fecha_fin], en formato .xlsx.
    """
    if fecha_inicio > fecha_fin:
        raise HTTPException(
            status_code=422,
            detail="'fecha_inicio' no puede ser posterior a 'fecha_fin'.",
        )

    creds = _get_creds_o_404(client_id)

    try:
        excel_file = generate_audit_report(
            creds,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )
    except ValueError as e:
        logger.error("Error de esquema en tn_sx_log del cliente '%s': %s", client_id, str(e))
        raise HTTPException(
            status_code=422,
            detail=f"La base de datos del cliente tiene un esquema inesperado: {str(e)}",
        )
    except Exception as e:
        logger.error("Error generando auditoría para client_id=%s: %s", client_id, str(e))
        raise HTTPException(
            status_code=503,
            detail="No se pudo generar el reporte de auditoría. Error al conectar con la base de datos del cliente.",
        )

    filename = f"auditoria_{client_id}_{fecha_inicio}_a_{fecha_fin}.xlsx"

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )