from fastapi import FastAPI
from fastapi.responses import RedirectResponse, HTMLResponse
from routers import users

app = FastAPI()

index_page_file = open("index.html")


@app.get("/", tags=["Default actions"], response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=index_page_file.read(), status_code=200)

app.include_router(users.router)
