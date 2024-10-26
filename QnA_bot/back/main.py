# back/main.py

from fastapi import FastAPI
from routes import main_router

app = FastAPI()

app.include_router(main_router)
