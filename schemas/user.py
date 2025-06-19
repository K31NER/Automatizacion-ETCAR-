from pydantic import BaseModel

class User_login(BaseModel):
    email: str
    password: str
    
class PersonalData(BaseModel):
    nombre: str
    correo: str
