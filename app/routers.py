# routers.py
from datetime import datetime, date, time
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from middleware import get_user_cookie
from models import Exercise, Series, Train, TrainExerciseView, TrainingAvailability, User
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

@router.post("/salvar_treino")
async def salvar_treino(
    request: Request,
    db: Session = Depends(get_db),
    cookie: dict = Depends(get_user_cookie),
):
    # Autenticação
    user_id = cookie.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")

    body = await request.json()
    train_id = body.get("train_id")
    exercicios = body.get("exercicios", [])
    inicio_iso = body.get("inicio")
    fim_iso = body.get("fim")
    total_sec = body.get("tempo_total_segundos")

    if train_id:
        # Atualiza treino existente
        treino_db = db.query(Train).filter(Train.id == train_id, Train.id_user == user_id).first()
        if not treino_db:
            raise HTTPException(status_code=404, detail="Treino não encontrado")
        try:
            # Update metadata
            if inicio_iso:
                dt_i = datetime.fromisoformat(inicio_iso.replace("Z", "+00:00"))
                treino_db.start_time = dt_i.time()
                treino_db.date = dt_i.date()
            if fim_iso:
                dt_f = datetime.fromisoformat(fim_iso.replace("Z", "+00:00"))
                treino_db.end_time = dt_f.time()
            if total_sec is not None:
                treino_db.expected_duration = int(total_sec)
            db.commit()
            # Remove old series
            db.query(Series).filter(Series.id_train == treino_db.id).delete()
            db.commit()
            # Insert new series
            for ex in exercicios:
                nome = ex.get("nome_exercicio")
                if not nome:
                    continue
                ex_model = db.query(Exercise).filter(Exercise.name == nome).first()
                if not ex_model:
                    ex_model = Exercise(name=nome)
                    db.add(ex_model)
                    db.commit()
                    db.refresh(ex_model)
                for s in ex.get("series", []):
                    new_s = Series(
                        id_train=treino_db.id,
                        id_exercise=ex_model.id,
                        weight=float(s.get("peso", 0)),
                        repetitions=int(s.get("reps", 0)),
                        rest_time=int(s.get("rest_time", 0)),
                    )
                    db.add(new_s)
            db.commit()
            return JSONResponse({"status": "ok", "train_id": treino_db.id})
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erro ao atualizar treino: {e}")
    else:
        # Cria novo treino
        nome_treino = body.get("nome_treino")
        if not nome_treino or not exercicios:
            raise HTTPException(status_code=400, detail="Payload incompleto para criar treino")
        try:
            dt_i = datetime.fromisoformat(inicio_iso.replace("Z", "+00:00")) if inicio_iso else datetime.now()
            dt_f = datetime.fromisoformat(fim_iso.replace("Z", "+00:00")) if fim_iso else datetime.now()
            new_train = Train(
                id_user=user_id,
                name=nome_treino,
                date=dt_i.date(),
                expected_duration=int(total_sec) if total_sec else None,
                start_time=dt_i.time(),
                end_time=dt_f.time(),
                feedback=None,
            )
            db.add(new_train)
            db.commit()
            db.refresh(new_train)
            # Insert series
            for ex in exercicios:
                nome = ex.get("nome_exercicio")
                ex_model = db.query(Exercise).filter(Exercise.name == nome).first()
                if not ex_model:
                    ex_model = Exercise(name=nome)
                    db.add(ex_model)
                    db.commit()
                    db.refresh(ex_model)
                for s in ex.get("series", []):
                    new_s = Series(
                        id_train=new_train.id,
                        id_exercise=ex_model.id,
                        weight=float(s.get("peso", 0)),
                        repetitions=int(s.get("reps", 0)),
                        rest_time=int(s.get("rest_time", 0)),
                    )
                    db.add(new_s)
            db.commit()
            return JSONResponse({"status": "ok", "train_id": new_train.id})
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erro ao salvar treino: {e}")