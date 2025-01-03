from fastapi.routing import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter()
    
@router.get("/project/{project_id}/browse", response_class=HTMLResponse)
async def read_item(project_id):
    with open("templates/file/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)
