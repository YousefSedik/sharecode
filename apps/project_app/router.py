from fastapi.routing import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

index_html = open("templates/project/index.html", encoding="UTF-8").read()
project_details_html = open(
    "templates/project/project-details.html", encoding="UTF-8"
).read()


@router.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(index_html)


@router.get("/project/{project_id}", response_class=HTMLResponse)
async def project_detail(project_id: str):
    return HTMLResponse(project_details_html)
