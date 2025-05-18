# routers.py
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from middleware import get_user_cookie
from models import TrainExerciseView, TrainingAvailability, User
from auxiliary import format_train_return
from database import get_db
from typing import Optional

router = APIRouter(
    prefix="/treino",
    tags=["treino"]
)

@router.get("")
async def get_all_treinos_by_user_id(
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

# Rota temporaria para teste - sempre vai retornar o mesmo treino em um json
@router.get("/treino")
async def get_treino(db: Session = Depends(get_db)):
    treino = {
  "treino-segunda": {
    "nome": "Peito, Ombro & Tríceps",
    "duracao-esperada": "60 minutos",
    "exercicios": [
      {
        "nome": "Supino Reto (Barra)",
        "sets": 4,
        "reps": 8,
        "descanso": "90 segundos",
        "carga": "65 kg"
      },
      {
        "nome": "Supino Inclinado (Halteres)",
        "sets": 3,
        "reps": 10,
        "descanso": "90 segundos",
        "carga": "22 kg"
      },
      {
        "nome": "Desenvolvimento Militar (Barra)",
        "sets": 4,
        "reps": 8,
        "descanso": "90 segundos",
        "carga": "45 kg"
      },
      {
        "nome": "Elevação Lateral (Halteres)",
        "sets": 3,
        "reps": 12,
        "descanso": "60 segundos",
        "carga": "10 kg"
      },
      {
        "nome": "Tríceps Testa (Barra EZ)",
        "sets": 3,
        "reps": 10,
        "descanso": "60 segundos",
        "carga": "30 kg"
      }
    ]
  },
  "treino-quarta": {
    "nome": "Costas & Bíceps",
    "duracao-esperada": "60 minutos",
    "exercicios": [
      {
        "nome": "Barra Fixa (Pegada Pronada)",
        "sets": 4,
        "reps": 8,
        "descanso": "90 segundos",
        "carga": "0 kg"
      },
      {
        "nome": "Remada Curvada (Barra)",
        "sets": 4,
        "reps": 8,
        "descanso": "90 segundos",
        "carga": "60 kg"
      },
      {
        "nome": "Pulldown (Puxador Frontal)",
        "sets": 3,
        "reps": 10,
        "descanso": "90 segundos",
        "carga": "70 kg"
      },
      {
        "nome": "Rosca Direta (Barra EZ)",
        "sets": 3,
        "reps": 10,
        "descanso": "60 segundos",
        "carga": "30 kg"
      },
      {
        "nome": "Rosca Martelo (Halteres)",
        "sets": 3,
        "reps": 12,
        "descanso": "60 segundos",
        "carga": "12 kg"
      }
    ]
  },
  "treino-sexta": {
    "nome": "Pernas & Ombros",
    "duracao-esperada": "60 minutos",
    "exercicios": [
      {
        "nome": "Agachamento Livre",
        "sets": 4,
        "reps": 8,
        "descanso": "120 segundos",
        "carga": "100 kg"
      },
      {
        "nome": "Leg Press",
        "sets": 4,
        "reps": 10,
        "descanso": "90 segundos",
        "carga": "180 kg"
      },
      {
        "nome": "Stiff (Halteres)",
        "sets": 3,
        "reps": 10,
        "descanso": "90 segundos",
        "carga": "30 kg"
      },
      {
        "nome": "Desenvolvimento Arnold (Halteres)",
        "sets": 3,
        "reps": 10,
        "descanso": "90 segundos",
        "carga": "20 kg"
      },
      {
        "nome": "Elevação Lateral Inclinada (Cabo)",
        "sets": 3,
        "reps": 12,
        "descanso": "60 segundos",
        "carga": "10 kg"
      }
    ]
  }
}
    return JSONResponse(content=jsonable_encoder(treino))