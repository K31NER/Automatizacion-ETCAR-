from sqlmodel import select
from utils.credential import *
from utils.manage_users import *
from fastapi import APIRouter,Request, Response
from fastapi.responses import JSONResponse
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
        
    return template.TemplateResponse("admin.html",{"request":request})

@router.get("/listar_trabajadores")
async def listar(db: session):
    """ Lista a todo los usuarios con rol de trabajador """
    users = db.exec(select(User.id, User.nombre, User.cargo).where(User.cargo == "Trabajador")).all()
    
    users_list = [{"id": user[0],"nombre":user[1], "cargo": user[2]} for user in users]
    return users_list

@router.get("/info_users")
async def info_users(db: session):
    """ Devulve el numero de usuarios totales y por roles """
    Total_users = len(db.exec(select(User.id)).all())
    Total_admin = len(db.exec(select(User.id).where(User.cargo== "Administrador")).all())
    Total_workers = len(db.exec(select(User.id).where(User.cargo== "Trabajador")).all())
    
    return JSONResponse(content={
        "users" : Total_users,
        "admins": Total_admin,
        "workes": Total_workers
    },status_code=200)
    
@router.get("/logout")
async def logout(response: Response):
    """ Cierra sesion y elimina el token de acceso """
    response = JSONResponse(content={
        "message": "Sesion cerrada correctamente"
    },status_code=200)
    response.delete_cookie("access_token", path="/")
    return response