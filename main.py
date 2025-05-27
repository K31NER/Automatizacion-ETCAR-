from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from db.db_config import create_tables
from routers import render,reportes,usuarios
from fastapi.templating import Jinja2Templates

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