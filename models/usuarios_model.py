from enum import Enum
from typing import Optional,TYPE_CHECKING,List
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.reportes_model import Reporte, Cronograma

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
    
    # Relación hacia Reporte y Cronograma
    reportes: List["Reporte"] = Relationship(back_populates="responsable")
    cronogramas: List["Cronograma"] = Relationship(back_populates="responsable")
    
    class Config:
        from_attributes = True
        
