from sqlmodel import select
from utils.clean_data import *
from utils.credential import *
from utils.manage_users import *
from models.reportes_model import *
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Response

router = APIRouter(tags=["Funciones extras"])

@router.get("/listar_trabajadores")
async def listar(db: session):
    """ Lista a todo los usuarios con rol de trabajador """
    users = db.exec(select(User.id, User.nombre, User.cargo, User.correo).where(User.cargo == "Trabajador")).all()
    
    users_list = [{"id": user[0],"nombre":user[1], "cargo": user[2], "correo": user[3]} for user in users]
    return users_list

@router.get("/info_users")
async def info_users(db: session):
    """ Devulve el numero de usuarios totales y por roles """
    Total_users = len(db.exec(select(User.id)).all())
    Total_admin = len(db.exec(select(User.id).where(User.cargo== "Administrador")).all())
    Total_workers = len(db.exec(select(User.id).where(User.cargo== "Trabajador")).all())
    
    return JSONResponse(content={
        "users" : Total_users,
        "admins": Total_admin,
        "workes": Total_workers
    },status_code=200)
    
@router.get("/list_report_user")
async def list_reports_user(db: session, user_id: int):
    """Devuelve todos los reportes de un usuario con el id proporcionado"""
    
    # Realizamos la consulta
    query = select(Reporte).where(Reporte.responsable_id == user_id)
    result = db.exec(query).all()
    
    # Validamos si existen los datos
    if not result:
        raise HTTPException(status_code=404,detail=f"No se encontraron reporte para este usuario")
    
    # Limpiamos los datos
    clean_data = await clean_orm_data(result)
    
    # Cambiamos el formato de fecha
    for data in clean_data:
        if isinstance(data.get("ultimo_mantenimiento"), datetime):
            data["ultimo_mantenimiento"] = data["ultimo_mantenimiento"].isoformat()
        if isinstance(data.get("proximo_mantenimiento"), datetime):
            data["proximo_mantenimiento"] = data["proximo_mantenimiento"].isoformat()

    return JSONResponse(content={"data": clean_data}, status_code=200)

@router.get("/list_cronograma_user")
async def list_reports_user(db: session, user_id: int):
    """Devuelve todos los cronograma de un usuario con el id proporcionado"""
    
    # Realizamos la consulata a la base de datos
    query = select(Cronograma).where(Cronograma.responsable_id == user_id)
    result = db.exec(query).all()
    
    # Validamos
    if not result:
        raise HTTPException(status_code=404,detail=f"No se encontraron cronogramas para este usuario")
    
    # Limpamos los datos
    clean_data = await clean_orm_data(result)

    # Cambiamos el formato de fecha
    for data in clean_data:
        if isinstance(data.get("prox_mantenimiento"), datetime):
            data["prox_mantenimiento"] = data["prox_mantenimiento"].isoformat()
            
    return JSONResponse(content={"data": clean_data}, status_code=200)

@router.get("/list_all_reports")
async def list_all_reports(db:session):
    """ Lista todos los reportes que estan en la base de datos """
    
    # Realizamos la consulta
    query = select(Reporte)
    result = db.exec(query).all()
    
    # Validamos
    if not result:
        raise HTTPException(status_code=404, detail="No se encontraron reportes")
    
    # Limpiamos los datos
    clean_data = await clean_orm_data(result)
    
    # Convertimos el formato de fecha
    for data in clean_data:
        if isinstance(data.get("ultimo_mantenimiento"), datetime):
            data["ultimo_mantenimiento"] = data["ultimo_mantenimiento"].isoformat()
        if isinstance(data.get("proximo_mantenimiento"), datetime):
            data["proximo_mantenimiento"] = data["proximo_mantenimiento"].isoformat()
            
    return JSONResponse(content={"data": clean_data}, status_code=200)

@router.get("/list_all_cronogramas")
async def list_all_cronogramas(db: session):
    """Devuelve todos los cronograma"""
    
    # Realizmos la consulta a la base de datos
    query = select(Cronograma)
    result = db.exec(query).all()
    
    # Validamos
    if not result:
        raise HTTPException(status_code=404, detail="No se encontraron cronogramas")
    
    # Limpiamos los datos
    clean_data = await clean_orm_data(result)
    
    # Cambiamos el formato de fecha
    for data in clean_data:
        if isinstance(data.get("prox_mantenimiento"), datetime):
            data["prox_mantenimiento"] = data["prox_mantenimiento"].isoformat()
            
    return JSONResponse(content={"data": clean_data}, status_code=200)

@router.get("/user_details")
async def user_details(db:session,user_id:int):
    """ Devuelve la informacion del usuario """
    
    # Obtenemos los reportes
    query_report = select(Reporte).where(Reporte.responsable_id == user_id)
    result_report = db.exec(query_report).all()
    
    # Obtenemos los cronogramas
    query_cronograma = select(Cronograma).where(Cronograma.responsable_id == user_id)
    result_cronograma = db.exec(query_cronograma).all()
    
    # Validamos
    if not result_report or not result_cronograma:
        raise HTTPException(status_code=404, detail="No se encontraron datos")
    # Limpiamos los datos
    reports = await clean_orm_data(result_report)
    cronogramas = await clean_orm_data(result_cronograma)
    
    # Convertimos el formato de fecha
    for data in reports:
        if isinstance(data.get("ultimo_mantenimiento"), datetime):
            data["ultimo_mantenimiento"] = data["ultimo_mantenimiento"].isoformat()
        if isinstance(data.get("proximo_mantenimiento"), datetime):
            data["proximo_mantenimiento"] = data["proximo_mantenimiento"].isoformat()
            
    for data in cronogramas:
        if isinstance(data.get("prox_mantenimiento"), datetime):
            data["prox_mantenimiento"] = data["prox_mantenimiento"].isoformat()
            
    return JSONResponse(content={
        "reports": reports,
        "cronogramas": cronogramas
    })
    
@router.get("/logout")
async def logout(response: Response):
    """ Cierra sesion y elimina el token de acceso """
    response = JSONResponse(content={
        "message": "Sesion cerrada correctamente"
    },status_code=200)
    response.delete_cookie("access_token", path="/")
    return response