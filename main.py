from fastapi import FastAPI
from db.db_config import create_tables
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers import render,reportes,usuarios,functions

app = FastAPI(title="MVP - Automatizacion ETCAR", 
            description="Proeycto de automatizacion",
            version="0.1",
            lifespan=create_tables
            )

templates = Jinja2Templates("templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluimos los routers
app.include_router(render.router)
app.include_router(reportes.router)
app.include_router(usuarios.router)
app.include_router(functions.router)