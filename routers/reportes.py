import pandas as pd
from io import BytesIO
from utils.pdf import *
from schemas.report import *
from fastapi import APIRouter
from utils.credential import *
from utils.clean_data import *
from utils.manage_users import *
from models.reportes_model import *
from fastapi.responses import JSONResponse,StreamingResponse

router = APIRouter(tags=["Reportes"])

@router.post("/new_registration")
async def save_registration(db:session,data: Create_report):
    """ Crea nuevos reportes de mantenimiento """
    # Validamos la entrada de tipo fecha
    try:
        # Convierte las cadenas de fecha a objetos datetime
        ultimo_mantenimiento = datetime.fromisoformat(data.fecha_ultimo)
        proximo_mantenimiento = datetime.fromisoformat(data.fecha_proximo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Formato de fecha incorrecto. Use el formato ISO 8601.")
    
    # Definimos el nuevo objeto de tipo reporte
    new_registration = Reporte(
        nombre_maquina = data.nombre_maquina,
        marca_modelo = data.marca,
        responsable_id = data.id,
        ubicacion = data.ubicacion,
        tipo_mantenimiento = data.tipo_mantenimiento,
        ultimo_mantenimiento = ultimo_mantenimiento,
        proximo_mantenimiento = proximo_mantenimiento,
        observacions= data.observaciones
    )
    
    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)
    
    return JSONResponse(content={
        "message": f"Registro del trabajador con id:{data.id} creado con exito"
    }, status_code=201)
    
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
    
@router.get("/download_report")
async def download_report(db:session,user_id:int):
    """ Descarga el excel con los reporte de el empleado con el id indicado """
    
    # Recuperamos la informacion de la base de datos
    query = select(Reporte).where(Reporte.responsable_id == user_id)
    reportes = db.exec(query).all()

    # Validamos los datos 
    if not reportes:
        raise HTTPException(status_code=404,detail=f"No se encontraron reportes para el usuario con id:{user_id}")
    
    # Limpiamos la informacion
    data_clean = await clean_orm_data(reportes)
    
    df = pd.DataFrame(data_clean) # Volvemos un df
    
    # Creamos el buffer para escribir el archivo en memoria
    output = BytesIO()
    
    # escribimos el archivo en el buffer
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name=f"reportes_usuario_{user_id}",index=False)
    
    # Reseteamos el puntero al inicio para leer todo
    output.seek(0)
    
    return StreamingResponse(
        output, status_code=200,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=reportes_usuario_{user_id}.xlsx"
        }
    )
    
@router.get("/download_cronograma")
async def download_cronograma(db:session,user_id:int):
    """ Descarga el cronograma del usuario con el id indicado """
    
    # Consulta a la base de datos
    query = select(Cronograma).where(Cronograma.responsable_id == user_id)
    cronogramas = db.exec(query).all()
    
    # Validamos que tenga cronogramas guardados
    if not cronogramas:
        raise HTTPException(status_code=404,detail=f"No se encontraron cronogramas para el usuario con id:{user_id}")
    
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
    
@router.get("/download_report_pdf")
async def download_pdf_report(db:session,user_id:int,admin_id:int):
    """ Crea el pdf en base a los reportes del usuario y pone las firmas"""
    
    # Obtenemos las firmas
    query_user = select(User).where(User.id == user_id)
    firma_user = db.exec(query_user).first()
    
    query_admin = select(User).where(User.id == admin_id)
    firma_admin = db.exec(query_admin).first()
    
    if not firma_user or not firma_admin:
        raise HTTPException(status_code=404,detail=f"No se encontraron firmas")
    
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
    query_report = select(Reporte).where(Reporte.responsable_id == user_id)
    reportes = db.exec(query_report)
    
    # Validamos los datos 
    if not reportes:
        raise HTTPException(status_code=404,detail=f"No se encontraron reportes para el usuario con id:{user_id}")
    
    # Limpiamos la informacion
    data_clean = await clean_orm_data(reportes)
    
    # Volvemos dataframe
    df = pd.DataFrame(data_clean)
    
    # Quitamos columnas innecesarias
    df.drop(columns=["id","responsable_id"],inplace=True)
    df.rename(columns={
    'marca_modelo': 'marca',
    'nombre_maquina': 'nombre',
    'ultimo_mantenimiento': 'ult_mant',
    'observacions': 'observaciones',
    'ubicacion': 'ubic',
    'tipo_mantenimiento': 'tipo_mant',
    'proximo_mantenimiento': 'prox_mant'
    }, inplace=True)
    
    # Generamos el pdf
    pdf_bytes = generar_pdf(df,firmas,"Reporte de maquinaria")
    buffer = BytesIO(pdf_bytes)
    
    # 6. Retornar el PDF como descarga
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=reporte_usuario_{user_id}.pdf"}
    )
    
@router.get("/download_cronograma_pdf")
async def download_pdf_report(db:session,user_id:int,admin_id:int):
    """ Crea el pdf en base a los cronogramas del usuario y pone las firmas"""
    
    # Obtenemos las firmas
    query_user = select(User).where(User.id == user_id)
    firma_user = db.exec(query_user).first()
    
    query_admin = select(User).where(User.id == admin_id)
    firma_admin = db.exec(query_admin).first()
    
    if not firma_user or not firma_admin:
        raise HTTPException(status_code=404,detail=f"No se encontraron firmas")
    
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
    cronogramas = db.exec(query_cronograma)
    
    # Validamos los datos 
    if not cronogramas:
        raise HTTPException(status_code=404,detail=f"No se encontraron cronogramas para el usuario con id:{user_id}")
    
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