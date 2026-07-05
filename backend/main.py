from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import APP_NAME
from app.database.database import Base, engine
from app.database import models
from app.routes.crm import router as crm_router
from app.routes.dashboard import router as dashboard_router
from app.routes.leads import router as leads_router
from app.routes.search import router as search_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title=APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leads_router)
app.include_router(search_router)
app.include_router(crm_router)
app.include_router(dashboard_router)


@app.get("/")
def home():
    return {"message": "Nestora AI backend is running"}