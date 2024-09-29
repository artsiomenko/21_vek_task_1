from fastapi import FastAPI
from app.routers import items
from app.database import engine
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(items.router)
