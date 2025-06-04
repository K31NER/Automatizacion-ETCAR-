from utils.clean_data import *
from utils.credential import *
from utils.manage_users import *
from models.reportes_model import *
from fastapi import APIRouter,Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Renderizado de html"])

template = Jinja2Templates(directory="templates")

@router.get("/",response_class=HTMLResponse)
async def login(request:Request):
    return template.TemplateResponse("login.html",{"request":request})

@router.get("/dashboard",response_class=HTMLResponse)
async def dashboard(request:Request, user:dict = Depends(get_current_user)):
    print(user)
    
    user_id = user.get("id")
    user_name = user.get("sub")
    user_role = user.get("role")
    
    if not user_id or not user_name or not user_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso autorizado a esta página"
        )
    return template.TemplateResponse("dashboard.html", {
        "request": request,
        "id":user_id ,
        "username": user_name,
        "rol": user_role
    })

    
@router.get("/reporte",response_class=HTMLResponse)
async def reporte(request:Request,user:dict = Depends(get_current_user)):
    user_id = user.get("id")
    user_name = user.get("sub")
    user_role = user.get("role")
    
    if not user_id or not user_name or not user_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso autorizado a esta página"
        )
    return template.TemplateResponse("reporte.html",{
        "request": request,
        "id":user_id,
        "username": user_name,
        "rol": user_role
    })


@router.get("/cronograma",response_class=HTMLResponse)
async def cronograma(request:Request,user:dict = Depends(get_current_user)):
    user_id = user.get("id")
    user_name = user.get("sub")
    user_role = user.get("role")
    
    if not user_id or not user_name or not user_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso autorizado a esta página"
        )
        
    return template.TemplateResponse("cronograma.html", {
        "request": request,
        "id":user_id,
        "username": user_name,
        "rol": user_role
    })

@router.get("/admin",response_class=HTMLResponse)
async def admin(request:Request,user:dict = Depends(required_admin)):
    user_id = user.get("id")
    user_name = user.get("sub")
    user_role = user.get("role")
    
    print(user)
    if not user_id or not user_name or not user_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso autorizado a esta página"
        )
        
    return template.TemplateResponse("admin.html",{"request":request,         
     "id":user_id ,
     "username": user_name,
     "rol": user_role})

