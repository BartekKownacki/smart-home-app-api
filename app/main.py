from fastapi import FastAPI
from fastapi.responses import RedirectResponse, HTMLResponse
from routers import users, acSocket, devices
from models.ACSocketStateModel import models as AcSocketStateModel
from models.UserModel import models as UserModel 
from database import engine

app = FastAPI()

AcSocketStateModel.Base.metadata.create_all(bind=engine)
UserModel.Base.metadata.create_all(bind=engine)

index_page_file = open("index.html")

@app.get("/", tags=["Default actions"], response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=index_page_file.read(), status_code=200)

app.include_router(users.router)
app.include_router(acSocket.router)
app.include_router(devices.router)
