import pandas as pd
import io
from app.models.db_config import get_client_engine

def generate_users_report(creds: dict):
    # 1. Crear motor dinámico para la base de datos del cliente
    engine = get_client_engine(creds)
    
    # 2. Query a la tabla real corregida
    query = "SELECT * FROM tn_user_lst"
    
    # 3. Lectura de datos
    df = pd.read_sql(query, engine)
    
    # 4. Mapeo exacto basado en la estructura tn_user_lst proporcionada
    column_mapping = {
        'id': 'ID Registro',
        'nombre': 'Nombre',
        'login': 'Login',
        'tipo_doc': 'Tipo de identificación',
        'identificacion': 'Número de identificación',
        'email': 'E-mail',
        'direccion': 'Dirección',
        'telefono': 'Teléfono',
        'pais': 'País',
        'departamento': 'Departamento',
        'ciudad': 'Municipio',
        'tipo': 'Tipo',
        'estado': 'Estado',
        'tipo_wf': 'Tipo de registro'
    }

    # Opcional: Transformar 'estado' de 1/0 a texto (quitar comentario si se desea)
    # df['estado'] = df['estado'].map({'1': 'Activo', '0': 'Inactivo', 1: 'Activo', 0: 'Inactivo'})

    # 5. Renombrar columnas
    # Usamos .reindex para asegurar que las columnas salgan en el orden exacto solicitado
    # y manejamos solo las columnas definidas en el mapeo
    df_final = df.rename(columns=column_mapping)
    
    # Seleccionamos solo las columnas resultantes del mapeo en el orden deseado
    columnas_finales = list(column_mapping.values())
    df_final = df_final[columnas_finales]
    
    # 6. Escribir a buffer de memoria (Excel .xlsx)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_final.to_excel(writer, index=False, sheet_name='Usuarios')
    
    output.seek(0)
    return output