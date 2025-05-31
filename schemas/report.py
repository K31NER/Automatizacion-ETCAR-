from pydantic import BaseModel

class Create_report(BaseModel):
    nombre_maquina: str
    ubicacion: str
    marca: str
    tipo_mantenimiento: str
    fecha_ultimo: str
    fecha_proximo: str
    observaciones: str
    
class Create_cronograma(BaseModel):
    nombre_maquina: str
    tarea_mantenimiento: str
    ubicacion: str
    marca: str
    frecuencia: str
    fecha_proximo: str
    estado : str