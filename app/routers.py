# routers.py
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from middleware import get_user_cookie
from models import TrainExerciseView, TrainingAvailability, User
from auxiliary import format_train_return, format_train_return_total
from database import get_db
from typing import Optional

router = APIRouter(
    prefix="/treino",
    tags=["treino"]
)

@router.get("")
async def get_all_treinos_by_user_id_ndays(
request: Request,
db: Session = Depends(get_db),
cookie: dict = Depends(get_user_cookie)  # This is the decoded cookie (JWT payload)
):
    try:
        user_id = cookie["id"]
        if not user_id:
            raise HTTPException(status_code=400, detail="Usuario não autenticado")
        user = db.query(User).filter(User.id == user_id).first()

        results = {}
        n_days = 0
        available_days = (
        db.query(TrainingAvailability)
        .filter(TrainingAvailability.id == user.id_dates) #Int representando id do user
        .distinct()
        .all())[0]
        for column in TrainingAvailability.__table__.columns.keys():
            if column != "id" and getattr(available_days, column) == 1:
                n_days += 1
                results[column] = {}

        subquery = (
        db.query(TrainExerciseView.train_id)
        .filter(TrainExerciseView.user_id == user.id)
        .distinct()
        .order_by(TrainExerciseView.train_id.desc())
        .limit(n_days)
        .subquery()
        )
        treinos = (
        db.query(TrainExerciseView)
        .filter(
        TrainExerciseView.user_id == user.id,
        TrainExerciseView.train_id.in_(subquery)
        )
        .all()
        )
        results = format_train_return(treinos, results)

        return JSONResponse(content=jsonable_encoder(results))

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/debug")
async def debug_view_test(db: Session = Depends(get_db)):
    #o int representa o id do usuario, que seria extraido do cookie
    results = {}
    n_days = 0
    user_id_debug = 30

    available_days = (
    db.query(TrainingAvailability)
    .filter(TrainingAvailability.id == user_id_debug) #Int representando id do user
    .distinct()
    .all())[0]
    for column in TrainingAvailability.__table__.columns.keys():
        if column != "id" and getattr(available_days, column) == 1:
            n_days += 1
            results[column] = {}

    subquery = (
        db.query(TrainExerciseView.train_id)
        .filter(TrainExerciseView.user_id == user_id_debug)
        .distinct()
        .order_by(TrainExerciseView.train_id.desc())
        .limit(n_days)
        .subquery()
    )
    treinos = (
        db.query(TrainExerciseView)
        .filter(
            TrainExerciseView.user_id == user_id_debug,
            TrainExerciseView.train_id.in_(subquery)
        )
        .all()
    )
    results = format_train_return(treinos, results)
    
    return JSONResponse(content=jsonable_encoder(results))

#get all treinos (feitos ou não)
@router.get("/all")
async def get_all_treinos_by_user_id(
request: Request,
db: Session = Depends(get_db),
cookie: dict = Depends(get_user_cookie)
):
    try:
        user_id = cookie["id"]
        if not user_id:
            raise HTTPException(status_code=400, detail="Usuario não autenticado")
        user = db.query(User).filter(User.id == user_id).first()

        results = {}

        treinos = (
        db.query(TrainExerciseView)
        .filter(
        TrainExerciseView.user_id == user.id
        )
        .all()
        )
        results = format_train_return_total(treinos, results)

        return JSONResponse(content=jsonable_encoder(results))

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))