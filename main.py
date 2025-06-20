from fastapi.responses import HTMLResponse
from db.db_config import create_tables
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI,HTTPException,Request, status
from routers import render,reportes,usuarios,functions,cronogramas

app = FastAPI(title="MVP - Automatizacion reportes de excel", 
            description="Proyecto de automatizacion de reportes de maquinaria",
            version="0.1",
            lifespan=create_tables
            )

templates = Jinja2Templates("templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluimos los routers
app.include_router(render.router)
app.include_router(usuarios.router)
app.include_router(reportes.router)
app.include_router(cronogramas.router)
app.include_router(functions.router)

# Manjeamos lso errores por credenciales invalidas
@app.exception_handler(HTTPException)
async def credenciales_invalidas(request:Request,exc:HTTPException):
    """ Renderiza html para informar sobre la falta de credenciales o permisos"""
    
    # Caputramos el tipo de error
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return templates.TemplateResponse(
            "no_autorizado.html",{"request":request},status_code=exc.status_code
        )
    # Validmos el otro tipo de error
    if exc.status_code == status.HTTP_403_FORBIDDEN:
        return templates.TemplateResponse(
            "alert_user.html",{"request":request},status_code=exc.status_code
        )