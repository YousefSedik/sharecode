from fastapi.routing import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter()

index_html = open("templates/file/index.html").read()

@router.get("/project/{project_id}/browse", response_class=HTMLResponse)
async def read_item(project_id):
    return HTMLResponse(content=index_html, status_code=200)
