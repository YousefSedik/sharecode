from fastapi.routing import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/project/index.html") as f:
        return HTMLResponse(f.read())


@router.get("/project/{project_id}", response_class=HTMLResponse)
async def project_detail(project_id: str):
    with open("templates/project/project-details.html") as f:
        return HTMLResponse(f.read())
