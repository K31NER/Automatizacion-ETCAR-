import bcrypt
import string
import secrets
from sqlmodel import select
from db.db_config import session
from models.usuarios_model import User
from fastapi import HTTPException, status

def hased_password(password:str) -> str:
    """ Hasear la contraseña del usuario 
    Parametros:
    - password : str
    """
    salt = bcrypt.gensalt()
    hased = bcrypt.hashpw(password.encode("utf-8"),salt)
    return hased.decode("utf-8")
    
def verify_password(plain_password:str,hased_password:str) -> bool:
    """ Verifica la contraseña del usuario 
    Parametros:
    - plain_password: str
    - hased_password: str
    """
    return bcrypt.checkpw(plain_password.encode("utf-8"),hased_password.encode("utf-8"))

def validate_user(db:session,email:str,password:str) -> User:
    """ Valida las credenciales del usuario 
    Parametros:
    - db: session
    - email: str
    - password: str
    """
    # Consulta para obtener el email
    query = select(User).where(User.correo == email)
    # Ejecutar la consulata
    result: User = db.exec(query).first()
    
    if not result or not verify_password(password, result.contraseña):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña incorrecta")
    
    return result

def random_password()-> str:
    """ Genera una contraseña aleatoria para los nuevos usuarios """
    
    return  ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(8))