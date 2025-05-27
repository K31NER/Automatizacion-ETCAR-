import os
from jose import jwt, JWTError
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, status
from datetime import datetime,timedelta,timezone

load_dotenv()

# Constantes
Secret_key = os.getenv("SECRET_KEY")
Algorithm = os.getenv("ALGORITHM")
Time = int(os.getenv("TIME","3600"))

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
def create_token(data:dict,time_expire:int = Time, 
                algorithm:str = Algorithm,
                secret_key:str = Secret_key) -> str:
    """ Crear JWT """
    
    data_copy = data.copy()
    if time_expire:
        data_copy.update({"exp":datetime.now(timezone.utc) + timedelta(seconds=time_expire)})
    
    encode_jwt = jwt.encode(data_copy, secret_key, algorithm=algorithm)
    
    return encode_jwt

def validate_token(jwt_token:str , secret_key = Secret_key, algorithm = Algorithm) -> dict:
    """ Valida el jwt """
    try:
        payload = jwt.decode(jwt_token,secret_key,algorithms=[algorithm])
        return payload
    except JWTError:
        raise credentials_exception
    
async def get_current_user(request: Request):
    """ Obtener el token del usuario """
    
    token = request.cookies.get("access_token")
    
    if not token:
        # Si no hay token en la cookie, intentar obtenerlo del encabezado de autorización
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    if not token:
        raise credentials_exception
    
    try:
        payload = validate_token(token)
        username: str = payload.get("sub")
        user_id: str = payload.get("id")
        role: str = payload.get("role")
        
        if username is None or user_id is None or role is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    return {"sub": username, "id": user_id, "role": role}

def required_admin(current_user: dict = Depends(get_current_user)) -> dict :
    """ Validar el rol de administrador """
    
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Acceso no autorizado"
        )
    return current_user