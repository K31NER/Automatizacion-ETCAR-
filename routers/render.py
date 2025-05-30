from utils.credential import *
from utils.manage_users import *
from fastapi import APIRouter,Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Renderizado de html"])

template = Jinja2Templates(directory="templates")

@router.get("/",response_class=HTMLResponse)
async def login(request:Request):
    return template.TemplateResponse("login.html",{"request":request})

@router.get("/dashboard",response_class=HTMLResponse)
async def dashboard(request:Request):
    return template.TemplateResponse("dashboard.html",{"request":request})

@router.get("/reporte",response_class=HTMLResponse)
async def reporte(request:Request):
    return template.TemplateResponse("reporte.html",{"request":request})

@router.get("/cronograma",response_class=HTMLResponse)
async def cronograma(request:Request):
    return template.TemplateResponse("cronograma.html",{"request":request})

@router.get("/admin",response_class=HTMLResponse)
async def admin(request:Request):
    return template.TemplateResponse("admin.html",{"request":request})