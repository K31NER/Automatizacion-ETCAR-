from schemas.user import * 
from utils.emails import *
from utils.clean_data import *
from utils.credential import *
from utils.manage_users import *
from db.db_config import session 
from models.usuarios_model import *
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Response , Form, UploadFile,File

router = APIRouter(tags=["Usuarios"])

# Schema de autenticacion
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@router.post("/login",summary="Manejo del registro de usuarios")
async def login(response: Response, db: session ,data: User_login):
    """ Maneja el registro de usuarios y crea el jwt"""
    
    email = data.email
    password = data.password
    user = validate_user(db,email,password)
    if not user:
        raise HTTPException(status_code=404,detail="Credenciales invalidas")
    
    # Creamos el token
    token_data = {"sub":user.nombre, "id": user.id ,"rol": user.cargo}
    token = create_token(token_data)
    # Preparamos un json para devolver datos relevantes
    response = JSONResponse(content={
        "message": "Inicio de sesion exitoso",
        "user": {
            "id": user.id,
            "nombre": user.nombre,
            "rol": user.cargo
        }
    })
    
    # Enviamos la cookie
    response.set_cookie("access_token",token,httponly=True,secure=True,samesite="strict")

    return response

@router.post("/signup",summary="Crear nuevos perfiles de usuarios")
async def singnup(db: session,user:dict = Depends(required_admin), 
                name: str = Form(...),
                rol: str = Form(...),
                email: str = Form(...),
                password: str = Form(...), 
                firma: UploadFile = File(...)):
    
    # Validamos y volvemos la foto bytes
    firma_content = await validar_tipo_archivo(firma)
    
    # Creamos el nuevo usuario
    new_user = User(
        nombre=name,
        correo=email,
        cargo=rol,
        contraseña= hased_password(password),
        firma=firma_content
    )
    
    # Guardamos los cambios
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Enviamos el correo de verificacion al nuevo usuario
    data_user = {
        "username":name,
        "email": email,
        "password":password
    }
    
    # Enviamos mensaje al nuevo usuario
    await enviar_correo_creacion(data_user,data_user["email"])
    
    return JSONResponse(content={
        "message": "Nuevo usuario creado con exito",
        "user": {
            "id": new_user.id,
            "nombre": new_user.nombre,
            "rol": new_user.cargo
        }
    },status_code=201)

@router.patch("/update_profile",summary="Actualizar los datos de los usuarios")
async def update_profile(db: session,
                user_id: int,
                name: Optional[str] = Form(None),
                email: Optional[str] = Form(None),
                password: Optional[str] = Form(None), 
                firma: Optional[UploadFile] = File(None),
                current_user: dict = Depends(get_current_user)):
    """ Actualiza la informacion de los usuarios"""
    
    # Obtenemos el usuario
    user = db.get(User,user_id)
    
    # Validamos el usuario
    if not user or user is None :
        return JSONResponse(status_code=404, content={"detail": f"No se encontró el usuario con id: {user_id}"})
    try: 
        
        # Definimos variables por si se cambia la contraseña o la firma
        cambio_password = False
        cambio_firma = False
        
        # Solo actualiza lo que realmente cambió
        if name is not None:
            user.nombre = name

        if email is not None:
            if current_user.get("rol") == "Administrador":
                user.correo = email
            else:
                raise HTTPException(status_code=403, detail="Solo un administrador puede cambiar el correo electrónico.")

        if password is not None:
            user.contraseña = hased_password(password) 
            cambio_password = True
            
        if firma is not None:
            firma_content = await validar_tipo_archivo(firma)
            user.firma = firma_content
            cambio_firma = True
        
        # Guardamos los cambios en la base de datos
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Enviamos el correo
        if cambio_firma or cambio_password:
            await enviar_correo_actualizacion(user.nombre,user.correo)
            
        return {
        "message": "Perfil actualizado exitosamente",
        "user": {
            "id": user.id,
            "nombre": user.nombre,
            "correo": user.correo
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error al actualizar datos: {e}")

@router.get("/gen_random_pass",summary="Generar contraseñas aletorias de 8 digitos")
async def create_random_pass():
    return JSONResponse(content={
        "password": random_password()
    }, status_code=201)
    
@router.delete("/workers/{worker_id}",summary="Borrar a los trabajadores por id")
async def delete_user(db: session,worker_id: int,user:dict = Depends(required_admin)):
    """ Borrar a los trabajadores en base a su id"""
    
    # Obtenemos el usuario en base a su id
    worker = db.get(User,worker_id)
    if not worker:
        return JSONResponse(status_code=404, content={"detail": f"No se encontró el usuario con id: {worker_id}"})
    
    # Validamos su rol
    if worker.cargo == "Administrador":
        return JSONResponse(status_code=403, content={"detail": f"No se puede eliminar a un administrador"})
    
    # Guardamos los registros del usuario eliminado antes de borrar
    await save_info_worker(db,worker_id,worker.nombre,worker.correo)
    
    # Borramos sus registros
    for crono in worker.cronogramas:
        db.delete(crono)
    for reporte in worker.reportes:
        db.delete(reporte)
        
    # Borramos al trabajador
    db.delete(worker)
    db.commit()
    
    # Le notificamos por correo
    await enviar_correo_eliminacion(username=worker.nombre,destinario=worker.correo)
    
    # Mostramos un mensaje
    return JSONResponse(content={
        "message" : f"El trabajador {worker.nombre} con id {worker.id} fue eliminado correctamente"
    })