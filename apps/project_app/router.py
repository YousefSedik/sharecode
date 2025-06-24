from fastapi.routing import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates/project")


@router.get("/", response_class=HTMLResponse)
async def index():
    return templates.TemplateResponse("index.html", {"request": {}})


@router.get("/project/{project_id}", response_class=HTMLResponse)
async def project_detail(project_id: str):
    return templates.TemplateResponse(
        "project-details.html", {"request": {}, "project_id": project_id}
    )
