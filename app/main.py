from fastapi import FastAPI, APIRouter
from fastapi.responses import RedirectResponse, HTMLResponse 
from fastapi.middleware.cors import CORSMiddleware
from routers import ledStrip, users, acSocket, devices, lightSocket, temphumid
from models.ACSocketStateModel import models as AcSocketStateModel
from models.UserModel import models as UserModel 
from models.LightSocketModel import models as LightSocketModel 
from models.LedStripModel import models as LedStripModel 
from models.TempHumidModel import models as TempHumidModel 
from models.DeviceModel import models as DeviceModel 
from database import engine

app = FastAPI() 

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DeviceModel.Base.metadata.create_all(bind=engine)
AcSocketStateModel.Base.metadata.create_all(bind=engine)
UserModel.Base.metadata.create_all(bind=engine)
LightSocketModel.Base.metadata.create_all(bind=engine)
LedStripModel.Base.metadata.create_all(bind=engine)
TempHumidModel.Base.metadata.create_all(bind=engine)

index_page_file = open("index.html")

router = APIRouter(
    tags=["Default actions"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=index_page_file.read(), status_code=200)

app.include_router(router)
app.include_router(devices.router)
app.include_router(users.router)
app.include_router(acSocket.router)
app.include_router(lightSocket.router)
app.include_router(ledStrip.router)
app.include_router(temphumid.router)


