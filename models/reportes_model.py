from enum import Enum
from typing import Optional
from datetime import datetime
from models.usuarios_model import User
from sqlmodel import SQLModel, Field, Relationship

# Clase para definir los tipo de mantenimiento
class Tipomantenimiento(str,Enum):
    preventivo = "Preventivo"
    correctivo = "Correctivo"
    instalacion = "Instalacion"
    revision = "Revision"
    
# Clase para definir los tipos de estados de las maquinas
class Estado(str,Enum):
    realizado = "Realizado"
    pendiente = "Pendiente"
    no_realizado = "No realizado"
    
# Molde general de las maquinas
class Maquina(SQLModel):
    nombre_maquina: str = Field()
    marca_modelo: str = Field()

    
# Clase de reportes de mantenimeintos
class Reporte(Maquina,table=True):
    id: int = Field(primary_key=True)
    responsable_id :int = Field(foreign_key="user.id")
    responsable: Optional[User] = Relationship(back_populates="reportes")
    ubicacion: str = Field()
    tipo_mantenimiento: Tipomantenimiento  = Field()
    ultimo_mantenimiento: datetime = Field()
    proximo_mantenimiento: datetime = Field()
    observacions: str = Field(max_length=100)
    class Config:
        from_attributes = True

# Clase de crogronogramas de mantenimientos
class Cronograma(Maquina,table=True):
    id: int = Field(primary_key=True)
    nombre_maquina: str = Field()
    marca_modelo: str = Field()
    responsable_id :int = Field(foreign_key="user.id")
    responsable: Optional[User] = Relationship(back_populates="cronogramas")
    ubicacion: str = Field()
    tarea_mantenimiento: str = Field(min_length=100)
    frecuencia: str = Field(max_length=1000)
    prox_mantenimiento : datetime = Field()
    estado: Estado = Field()
    
    class Config:
        from_attributes = True