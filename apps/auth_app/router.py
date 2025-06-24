from fastapi.routing import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates/auth")
router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login():
    return templates.TemplateResponse("login.html", {"request": {}})


@router.get("/sign-up", response_class=HTMLResponse)
async def register():
    return templates.TemplateResponse("signup.html", {"request": {}})
