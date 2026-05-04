from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from app.services.config_service import get_db_credentials
from app.services.excel_service import generate_users_report

router = APIRouter()

@router.get("/export-users")
def export_users(client_id: str = Query(...)):
    # 1. Obtener credenciales de la BD1 usando el client_id
    creds = get_db_credentials(client_id)
    
    if not creds:
        raise HTTPException(status_code=404, detail="Client ID no encontrado en configuración.")
    
    # 2. Generar el archivo Excel desde la BD2
    excel_file = generate_users_report(creds)
    
    # 3. Retornar el archivo para descarga inmediata
    filename = f"reporte_usuarios_{client_id}.xlsx"
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )