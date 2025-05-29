from schemas.user import * 
from utils.credential import *
from utils.manage_users import *
from db.db_config import session 
from models.usuarios_model import *
from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

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