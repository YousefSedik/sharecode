from fastapi.routing import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates/file")
router = APIRouter()


@router.get("/project/{project_id}/browse", response_class=HTMLResponse)
async def read_item(project_id):
    return templates.TemplateResponse(
        "index.html", {"request": {}, "project_id": project_id}
    )
