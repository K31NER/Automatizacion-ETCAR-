from utils.credential import *
from utils.manage_users import *
from fastapi import APIRouter,Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

template = Jinja2Templates(directory="templates")

router = APIRouter(tags=["Renderizado de html"])

@router.get("/",response_class=HTMLResponse)
async def login(request:Request):
    return template.TemplateResponse("login.html",{"request":request})

@router.get("/dashboard",response_class=HTMLResponse)
async def dashboard(request:Request):
    return template.TemplateResponse("dashboard.html",{"request":request})

@router.get("/reporte",response_class=HTMLResponse)
async def reporte(request:Request):
    return template.TemplateResponse("reporte.html",{"request":request})