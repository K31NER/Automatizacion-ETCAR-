from typing import List, TypeVar
from models.reportes_model import *

T = TypeVar("T")  # Genérico para cualquier clase ORM

async def clean_orm_data(data:List[T]) -> list[dict]:
    """ Limpa los datos que vienen en tipo ORM """
    try:
        # Volvemos diccionario
        data_ditc = [reporte.__dict__ for reporte in data]
        
        # Terminamos de limpiar
        for data in data_ditc:
            data.pop("_sa_instance_state",None)
            
            for key, value in data.items():
                # Si el valor es una instancia de Enum, lo transformamos
                if isinstance(value, Enum):
                    data[key] = value.value
                    
        # Devolvemos los datos limpios
        return data_ditc
    
    except AttributeError as e:
        raise ValueError("Los objetos proporcionados no parecen ser instancias válidas del modelo Reporte.") from e
    except Exception as e:
        raise RuntimeError("Ocurrió un error inesperado al limpiar los datos del reporte.") from e