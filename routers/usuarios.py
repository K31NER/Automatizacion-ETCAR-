from fastapi import APIRouter
from utils.credential import *
from utils.manage_users import *
from models.usuarios_model import *

router = APIRouter(tags=["Usuarios"])

