from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field

# manejo de roles
class CargoEnum(str,Enum):
    admin = "Administrador"
    trabajador = "Trabajador"
    
# Clase base de usuarios
class UserBase(SQLModel):
    nombre: str = Field()
    correo: str = Field(unique=True)
    cargo: CargoEnum = Field(default=CargoEnum.trabajador)
    firma: Optional[bytes] = Field(default=None)
    
# Clase para crear usuarios
class CreateUser(UserBase):
    contraseña: str = Field()

class UserRead(UserBase):
    id: int
# Clase para crear la tabla
class User(CreateUser,table=True):
    id: Optional[int] = Field(primary_key=True)
    
    class Config:
        from_attributes = True
        
