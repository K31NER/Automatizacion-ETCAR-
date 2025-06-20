from schemas.user import * 
from utils.credential import *
from utils.manage_users import *
from db.db_config import session 
from models.usuarios_model import *
from utils.emails import enviar_correo
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Response , Form, UploadFile,File

router = APIRouter(tags=["Usuarios"])

# Schema de autenticacion
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@router.post("/login")
async def login(response: Response, db: session ,data: User_login):
    email = data.email
    password = data.password
    user = validate_user(db,email,password)
    if not user:
        raise HTTPException(status_code=404,detail="Credenciales invalidas")
    
    # Creamos el token
    token_data = {"sub":user.nombre, "id": user.id ,"role": user.cargo}
    token = create_token(token_data)
    # Preparamos un json para devolver datos relevantes
    response = JSONResponse(content={
        "message": "Inicio de sesion exitoso",
        "user": {
            "id": user.id,
            "nombre": user.nombre,
            "role": user.cargo
        }
    })
    
    # Enviamos la cookie
    response.set_cookie("access_token",token,httponly=True,secure=True,samesite="strict")

    return response

@router.post("/signup")
async def singnup(db: session, 
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
    await enviar_correo(data_user,data_user["email"])
    
    return JSONResponse(content={
        "message": "Nuevo usuario creado con exito",
        "user": {
            "id": new_user.id,
            "nombre": new_user.nombre,
            "rol": new_user.cargo
        }
    },status_code=201)

@router.patch("/update_profile")
async def update_profile(db: session,
                user_id: int,
                name: Optional[str] = Form(None),
                email: Optional[str] = Form(None),
                password: Optional[str] = Form(None), 
                firma: Optional[UploadFile] = File(None)):
    """ Actualiza la informacion de los usuarios"""
    
    # Obtenemos el usuario
    user = db.get(User,user_id)
    
    # Validamos el usuario
    if not user or user is None :
        return JSONResponse(status_code=404, content={"detail": f"No se encontró el usuario con id: {user_id}"})
    try: 
        # Solo actualiza lo que realmente cambió
        if name is not None:
            user.nombre = name

        if email is not None:
            user.correo = email

        if password is not None:
            user.contraseña = hased_password(password) 
            
        if firma is not None:
            firma_content = await validar_tipo_archivo(firma)
            user.firma = firma_content
        
        # Guardamos los cambios en la base de datos
        db.add(user)
        db.commit()
        db.refresh(user)
        
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