# routers.py
import logging
import traceback
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from middleware import get_user_cookie
from models import (
    Exercise,
    Series,
    Train,
    TrainExerciseView,
    TrainingAvailability,
    User,
)
from datetime import datetime
from auxiliary import format_train_return, format_train_return_total
from database import get_db
from typing import Optional

router = APIRouter(prefix="/treino", tags=["treino"])


@router.get("")
async def get_all_treinos_by_user_id_ndays(
    request: Request,
    db: Session = Depends(get_db),
    cookie: dict = Depends(get_user_cookie),  # This is the decoded cookie (JWT payload)
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
            .filter(
                TrainingAvailability.id == user.id_dates
            )  # Int representando id do user
            .distinct()
            .all()
        )[0]
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
                TrainExerciseView.train_id.in_(subquery),
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
    # o int representa o id do usuario, que seria extraido do cookie
    results = {}
    n_days = 0
    user_id_debug = 30

    available_days = (
        db.query(TrainingAvailability)
        .filter(
            TrainingAvailability.id == user_id_debug
        )  # Int representando id do user
        .distinct()
        .all()
    )[0]
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
            TrainExerciseView.train_id.in_(subquery),
        )
        .all()
    )
    results = format_train_return(treinos, results)

    return JSONResponse(content=jsonable_encoder(results))


# get all treinos (feitos ou não)
@router.get("/all")
async def get_all_treinos_by_user_id(
    request: Request,
    db: Session = Depends(get_db),
    cookie: dict = Depends(get_user_cookie),
):
    try:
        user_id = cookie.get("id")
        if not user_id:
            raise HTTPException(status_code=400, detail="Usuario não autenticado")

        user = db.query(User).filter(User.id == user_id).first()

        treinos = (
            db.query(TrainExerciseView)
            .filter(TrainExerciseView.user_id == user.id)
            .all()
        )
        # Chama apenas com a lista de treinos, conforme nova assinatura
        results = format_train_return_total(treinos)

        return JSONResponse(content=jsonable_encoder(results))

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conclude_train")
async def conclude_train(
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

    if not train_id or not isinstance(train_id, int) or train_id <= 0: # Exemplo de validação mais estrita
        raise HTTPException(status_code=400, detail="train_id é obrigatório e deve ser um inteiro positivo")
    
    inicio_iso = body.get("inicio")
    fim_iso = body.get("fim")

    if train_id:
        # Atualiza treino existente
        treino_db = db.query(Train).filter(Train.id == train_id).first()
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
            db.commit()
            db.flush()

            return JSONResponse({"status": "ok", "train_id": train_id})
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erro ao salvar treino: {e}")


@router.post("/change_train_values")
async def change_train_values(
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

    if (
        not train_id or not isinstance(train_id, int) or train_id <= 0
    ):  # Exemplo de validação mais estrita
        raise HTTPException(
            status_code=400,
            detail="train_id é obrigatório e deve ser um inteiro positivo",
        )
    exercicios = body.get("exercicios")

    if train_id:
        # Seleciona todas as séries do treino
        try:
            for exercicio in exercicios:
                exercicio_db = (
                    db.query(Exercise)
                    .filter(Exercise.name == exercicio["nome_exercicio"])
                    .first()
                )
                series = (
                    db.query(Series)
                    .filter(
                        Series.id_train == train_id,
                        Series.id_exercise == exercicio_db.id,
                    )
                    .all()
                )
                counter_serie = 0
                for serie in series:
                    if counter_serie >= len(exercicio["series"]):
                        db.query(Series).filter(Series.id == serie.id).delete()
                    else:
                        serie.weight = exercicio["series"][counter_serie]["peso"]
                        serie.repetitions = exercicio["series"][counter_serie]["reps"]
                        counter_serie += 1
            db.commit()

            return JSONResponse({"status": "ok", "train_id": train_id})
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erro ao salvar treino: {e}")


# Rota para criar um novo treino baseado no treino que o user acabou de concluir
# O objetivo é criar um novo treino com os mesmos exercícios e séries do treino concluído,
# porém atualizando o nome do treino e a data e a quantidade de repetições e pesos por série
# para o usuário evoluir com os treinos
@router.post("/evo")
async def evo_train(
    request: Request,
    db: Session = Depends(get_db),
    cookie: dict = Depends(get_user_cookie),
):
    # 1) Autenticação
    user_id = cookie.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")

    # 2) Recebe o train_id
    body = await request.json()
    prev_train_id = body.get("train_id")
    if not prev_train_id:
        raise HTTPException(status_code=400, detail="train_id é obrigatório")

    # 3) Busca as séries do treino anterior
    prev_series = (
        db.query(Series)
        .filter(Series.id_train == prev_train_id)
        .order_by(Series.id_exercise, Series.id)
        .all()
    )
    if not prev_series:
        raise HTTPException(
            status_code=404, detail="Nenhuma série encontrada para o treino"
        )

    try:
        # 4) Cria novo Train de evolução
        prev_train = db.query(Train).filter(Train.id == prev_train_id).first()
        new_train = Train(
            id_user=user_id,
            name=f"{prev_train.name}",
            date=datetime.now().date(),
            expected_duration=prev_train.expected_duration,
            start_time=None,
            end_time=None,
            feedback=None,
        )
        db.add(new_train)
        db.commit()
        db.refresh(new_train)

        # 5) Aplica progressão e insere as novas séries
        for s in prev_series:
            if s.repetitions >= 16:
                new_reps = 10
                new_weight = s.weight + 2
            else:
                new_reps = s.repetitions + 1
                new_weight = s.weight

            new_series = Series(
                id_train=new_train.id,
                id_exercise=s.id_exercise,
                weight=new_weight,
                repetitions=new_reps,
                rest_time=s.rest_time,
            )
            db.add(new_series)

        db.commit()
        return JSONResponse({"status": "ok", "new_train_id": new_train.id})

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao criar treino de evolução: {e}"
        )
