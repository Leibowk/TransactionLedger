from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import endpoints
from .config import get_app_config

app_config = get_app_config()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router)


@app.get("/")
async def read_root():
    return {"message": "TransactionLedger API is running."}
