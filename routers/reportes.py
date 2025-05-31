from schemas.report import *
from fastapi import APIRouter
from utils.credential import *
from utils.manage_users import *
from models.reportes_model import *
from fastapi.responses import JSONResponse

router = APIRouter(tags=["Reportes"])

@router.post("/new_registration")
async def save_registration(db:session,data: Create_report, user_id:int):
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
        responsable_id = user_id,
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
        "message": f"Registro del trabajador con id:{user_id} creado con exito"
    }, status_code=201)
    
@router.post("/new_cronograma")
async def save_cronograma(db:session,data: Create_cronograma, user_id:int):
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
        responsable_id = user_id,
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
        "message": f"Registro del trabajador con id:{user_id} creado con exito"
    }, status_code=201)