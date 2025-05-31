from schemas.user import * 
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
    
    return JSONResponse(content={
        "message": "Nuevo usuario creado con exito",
        "user": {
            "id": new_user.id,
            "nombre": new_user.nombre,
            "rol": new_user.cargo
        }
    },status_code=201)
