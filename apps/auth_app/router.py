from fastapi.routing import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()
login_html = open("templates/auth/login.html", encoding="UTF-8").read()
signup_html = open("templates/auth/signup.html", encoding="UTF-8").read()


@router.get("/login", response_class=HTMLResponse)
async def login():
    return HTMLResponse(login_html)


@router.get("/sign-up", response_class=HTMLResponse)
async def register():
    return HTMLResponse(signup_html)
