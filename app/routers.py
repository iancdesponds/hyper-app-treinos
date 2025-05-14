# routers.py
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from middleware import auth_needed
from models import TrainExerciseView
from database import get_db
from typing import Optional

router = APIRouter(
    prefix="/treino",
    tags=["treino"]
)

@router.get("/")
@auth_needed
async def get_all_treinos_by_user_id(
    request: Request,
    db: Session = Depends(get_db),
    cookie: Optional[dict] = None
):
    try:
        user_id = cookie.get("id")
        if not user_id:
            raise HTTPException(status_code=400, detail="Usuario não autenticado")

        treinos = db.query(TrainExerciseView).filter(TrainExerciseView.user_id == user_id).all()

        return JSONResponse(content=jsonable_encoder(treinos))

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/debug")
async def debug_view_test(db: Session = Depends(get_db)):
    #o int representa o id do usuario, que seria extraido do cookie
    treinos = db.query(TrainExerciseView).filter(TrainExerciseView.user_id == 1).all()
    return JSONResponse(content=jsonable_encoder(treinos))
