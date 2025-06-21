import pandas as pd
from io import BytesIO
from sqlmodel import select
from db.db_config import session
from typing import List, TypeVar
from models.reportes_model import *
from datetime import datetime , timezone
from fastapi.responses import JSONResponse

T = TypeVar("T")  # Genérico para cualquier clase ORM

async def clean_orm_data(data:List[T]) -> list[dict]:
    """ Limpa los datos que vienen en tipo ORM """
    try:
        # Volvemos diccionario
        data_ditc = [reporte.__dict__ for reporte in data]
        
        # Terminamos de limpiar
        for data in data_ditc:
            data.pop("_sa_instance_state",None)
            
            for key, value in data.items():
                # Si el valor es una instancia de Enum, lo transformamos
                if isinstance(value, Enum):
                    data[key] = value.value
                    
        # Devolvemos los datos limpios
        return data_ditc
    
    except AttributeError as e:
        raise ValueError("Los objetos proporcionados no parecen ser instancias válidas del modelo Reporte.") from e
    except Exception as e:
        raise RuntimeError("Ocurrió un error inesperado al limpiar los datos del reporte.") from e
    
# Guardamos la informacion del usuario eliminado
async def save_info_worker(db:session,worker_id:int,username:str,usermail:str):
    """ Genera un excel general con los reportes del usuario eliminado """
    
    # Obtenemos los reportes
    query_reports = select(Reporte).where(Reporte.responsable_id == worker_id)
    reportes = db.exec(query_reports).all()
    
    # Obtemos los cronogramas
    query_crono  = select(Cronograma).where(Cronograma.responsable_id == worker_id)
    cronogramas = db.exec(query_crono).all()
    
    # Validamos los datos 
    if not reportes and not cronogramas:
        return JSONResponse(status_code=404, content={"detail": f"No se encontró registros para el usuario con id: {worker_id}"})
    
    # Hacemos copias antes de tocar la sesión
    reportes_copy = list(reportes) if reportes else []
    cronogramas_copy = list(cronogramas) if cronogramas else []
    
    # Limpiamos los datos
    data_clean_report = await clean_orm_data(reportes_copy)
    data_clean_crono = await clean_orm_data(cronogramas_copy)
    
    # Volvemos un df
    df_report = pd.DataFrame(data_clean_report) 
    df_crono = pd.DataFrame(data_clean_crono)
    
    # Agregamos la nueva columna de tipo
    df_report['tipo'] = 'Reporte'
    df_crono['tipo'] = 'Cronograma'
    
    # Juntamos los datos en un solo excel
    df = pd.concat([df_report, df_crono], ignore_index=True)
    
    # Rellenamos NaN con un mensaje claro
    df.fillna("No aplica", inplace=True)
    
    # Agregamos una columans con el nombre de usuario
    df["Nombre responsable"] = username
    
    # Creamos el buffer para escribir el archivo en memoria
    output = BytesIO()
    
    # escribimos el archivo en el buffer
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name=f"historico_usuario_{worker_id}",index=False)
    
    # Reseteamos el puntero al inicio para leer todo
    output.seek(0)
    
    # guardamos en la base de datos
    new_record = Registro(
        nombre=username,
        correo=usermail,
        registro= output.read()
    )
    
    # Realizamos el guardado en la base de datos
    try:
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"detail": f"Error al guardar el registro: {str(e)}"})
    finally:
        db.expunge(new_record)
        
    return JSONResponse(status_code=200, content={"detail": "Registro actualizado con éxito"})