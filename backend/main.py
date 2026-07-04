from app.routes.search import router as search_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.leads import router as leads_router

from app.config import APP_NAME

app = FastAPI(title=APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leads_router)
app.include_router(search_router)

@app.get("/")
def home():
    return {"message": "Nestora AI backend is running"}