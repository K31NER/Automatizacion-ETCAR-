from typing import Annotated
from fastapi import FastAPI, Depends
from sqlmodel import Session,create_engine,SQLModel

URL = "sqlite:///./Test.db"

engine = create_engine(URL,connect_args={"check_same_thread": False},echo=True)

def get_session():
    """ Obtener la conexion de la base de datos"""
    with Session(engine) as session:
        yield session

def create_tables(app:FastAPI):
    """ Crea todas las tablas de la base de datos """
    SQLModel.metadata.create_all(engine)
    print("Tablas creadas")
    yield
    
# Obtener la session de la base de datos
session = Annotated[Session,Depends(get_session)]