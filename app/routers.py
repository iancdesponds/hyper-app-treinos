from fastapi import APIRouter
from dotenv import load_dotenv
import os

load_dotenv()
train_ai = os.getenv("TRAIN_AI_ROUTE")

router = APIRouter(
    prefix="/treino",
    tags=["treino"]
)

@router.get("/ping")
def ping():
    return {"message": "pong"}
