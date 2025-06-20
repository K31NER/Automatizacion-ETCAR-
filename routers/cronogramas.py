import pandas as pd
from io import BytesIO
from utils.pdf import *
from schemas.report import *
from utils.credential import *
from utils.clean_data import *
from utils.manage_users import *
from models.reportes_model import *
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse,StreamingResponse

router = APIRouter(tags=["Cronogramas"])

@router.post("/new_cronograma")
async def save_cronograma(db:session,data: Create_cronograma):
    """ Crea nuevos reportes de mantenimiento """
    # Validamos la entrada de tipo fecha
    try:
        # Convierte las cadenas de fecha a objetos datetime
        proximo_mantenimiento = datetime.fromisoformat(data.fecha_proximo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Formato de fecha incorrecto. Use el formato ISO 8601.")
    
    # Definimos el nuevo objeto de tipo Cronograma
    new_registration = Cronograma(
        nombre_maquina = data.nombre_maquina,
        marca_modelo = data.marca,
        responsable_id = data.id,
        ubicacion = data.ubicacion,
        tarea_mantenimiento=data.tarea_mantenimiento,
        prox_mantenimiento = proximo_mantenimiento,
        estado = data.estado,
        frecuencia= data.frecuencia
    )
    
    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)
    
    return JSONResponse(content={
        "message": f"Cronograma del trabajador con id:{data.id} creado con exito"
    }, status_code=201)
    
@router.get("/download_cronograma")
async def download_cronograma(db:session,user_id:int):
    """ Descarga el cronograma del usuario con el id indicado """
    
    # Consulta a la base de datos
    query = select(Cronograma).where(Cronograma.responsable_id == user_id)
    cronogramas = db.exec(query).all()
    
    # Validamos que tenga cronogramas guardados
    if not cronogramas:
        return JSONResponse(status_code=404, content={"detail": f"No se encontró el cronograma para usuario con id: {user_id}"})
    
    # Preparamos los datos
    data_clean = await clean_orm_data(cronogramas)
    df = pd.DataFrame(data_clean)
    
    # Definimos el buffer para escribir en memoria
    output = BytesIO()
    
    # Escribimos en el buffer
    with pd.ExcelWriter(output,engine="xlsxwriter") as writer:
        df.to_excel(writer,"cronograma_usuario_{user_id}",index=False)
    
    # Reseteamos el buffer
    output.seek(0)
    
    return StreamingResponse(
        output, status_code=200,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=cronogranma_usuario_{user_id}.xlsx"
        }
    )

@router.get("/download_cronograma_pdf")
async def download_pdf_cronograma(db:session,user_id:int,admin_id:int):
    """ Crea el pdf en base a los cronogramas del usuario y pone las firmas"""
    # Obtenemos las firmas
    query_user = select(User).where(User.id == user_id)
    firma_user = db.exec(query_user).first()
    
    query_admin = select(User).where(User.id == admin_id)
    firma_admin = db.exec(query_admin).first()
    
    if not firma_user or not firma_admin:
        return JSONResponse(status_code=404, content={"detail": f"No se encontró el usuario con id: {user_id}"})
    
    # 2. Firmas formateadas
    firmas = []
    for u in [firma_user, firma_admin]:
        if not u.firma:
            raise HTTPException(status_code=400, detail=f"El usuario {u.nombre} no tiene firma registrada.")
        firmas.append({
            "nombre": u.nombre,
            "imagen_base64": firma_bytes_a_base64(u.firma)
        })
    
    # Obtenemos los datos
    query_cronograma = select(Cronograma).where(Cronograma.responsable_id == user_id)
    cronogramas = db.exec(query_cronograma).all()
    
    # Validamos los datos 
    if not cronogramas:
        return JSONResponse(status_code=404, content={"detail": f"No se encontraron cronogramas"})
    
    # Limpiamos la informacion
    data_clean = await clean_orm_data(cronogramas)
    
    # Volvemos dataframe
    df = pd.DataFrame(data_clean)
    
    # Quitamos columnas innecesarias
    df.drop(columns=["id","responsable_id"],inplace=True)
    # Generamos el pdf
    pdf_bytes = generar_pdf(df,firmas,"Cronograma de maquinaria")
    buffer = BytesIO(pdf_bytes)
    
    # 6. Retornar el PDF como descarga
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=cronograma_usuario_{user_id}.pdf"}
    )
    


# EDITAR CRONOGRAMA
@router.put("/edit_cronograma/{id}")
async def edit_cronograma(id: int, data: Create_cronograma, db: session):
    cronograma = db.get(Cronograma, id)
    if not cronograma:
        return JSONResponse(status_code=404, content={"detail": f"No se encontró el cronograma con id: {id}"})
    try:
        cronograma.nombre_maquina = data.nombre_maquina
        cronograma.marca_modelo = data.marca
        cronograma.responsable_id = data.id
        cronograma.ubicacion = data.ubicacion
        cronograma.tarea_mantenimiento = data.tarea_mantenimiento
        cronograma.prox_mantenimiento = datetime.fromisoformat(data.fecha_proximo)
        cronograma.estado = data.estado
        cronograma.frecuencia = data.frecuencia
        db.commit()
        db.refresh(cronograma)
        return JSONResponse(content={"message": "Cronograma actualizado correctamente"}, status_code=200)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al actualizar: {str(e)}")

# ELIMINAR CRONOGRAMA
@router.delete("/delete_cronograma/{id}")
async def delete_cronograma(id: int, db: session):
    cronograma = db.get(Cronograma, id)
    if not cronograma:
        return JSONResponse(status_code=404, content={"detail": f"No se encontró el cronograma con id: {id}"})
    try:
        db.delete(cronograma)
        db.commit()
        return JSONResponse(content={"message": "Cronograma eliminado correctamente"}, status_code=200)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al eliminar: {str(e)}")