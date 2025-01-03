from fastapi.routing import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login():
    print("Login page")
    with open("templates/auth/login.html") as f:
        return HTMLResponse(f.read())

@router.get("/sign-up", response_class=HTMLResponse)
async def register():
    with open("templates/auth/signup.html") as f:
        return HTMLResponse(f.read())
