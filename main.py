from fastapi import FastAPI
from routers import render,reportes,usuarios

app = FastAPI(title="MVP - Automatizacion ETCAR", 
            description="Proeycto de automatizacion",
            version="0.1",
            #lifespan=
            )

# Incluimos los routers
app.include_router(render.router)
app.include_router(reportes.router)
app.include_router(usuarios.router)