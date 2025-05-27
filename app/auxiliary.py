from models import TrainExerciseView

def format_train_return(treinos, results):
    train_map = {}
    for t in treinos:
        train_id = t.train_id
        if train_id not in train_map:
            train_map[train_id] = []
        train_map[train_id].append(t)

    ordered_train_ids = list(train_map.keys())
    ordered_days = list(results.keys())

    for day, train_id_do_dia in zip(ordered_days, ordered_train_ids):
        treinos_do_dia = train_map[train_id_do_dia]
        if treinos_do_dia:
            # Supondo que TrainExerciseView tenha os campos necessários ou que você os adicione
            # se eles forem fixos para o treino (ex: train_calories, train_muscle_groups, etc.)
            primeiro_registro_treino = treinos_do_dia[0]

            results[day] = {
                "id": train_id_do_dia,  # <--- ADICIONADO O ID DO TREINO AQUI
                "name": primeiro_registro_treino.train_name,
                "expected_duration": primeiro_registro_treino.expected_duration,
                # Adicione outros campos se necessário e se estiverem disponíveis em TrainExerciseView
                # Por exemplo, se sua view tem 'train_calories', 'train_muscle_groups', 'train_last_executed':
                # "calories": primeiro_registro_treino.train_calories,
                # "muscle_groups": primeiro_registro_treino.train_muscle_groups, # Pode precisar de parsing se for string JSON
                # "last_executed": primeiro_registro_treino.train_last_executed.isoformat() if primeiro_registro_treino.train_last_executed else None,
                "exercises": []
            }
            
            grouped_exercises = {}
            for t_serie in treinos_do_dia:
                name = t_serie.exercise_name
                if name not in grouped_exercises:
                    grouped_exercises[name] = {
                        "exercise_name": name,
                        "reps": [],
                        "weight": [],
                        "rest": []
                    }
                grouped_exercises[name]["reps"].append(t_serie.exercise_repetitions)
                grouped_exercises[name]["weight"].append(t_serie.exercise_weight)
                grouped_exercises[name]["rest"].append(t_serie.exercise_rest)
            
            results[day]["exercises"] = list(grouped_exercises.values())
    return results


def format_train_return_total(treinos):
    # Prepare maps for complete and incomplete trainings
    train_map = {"Complete": {}, "Incomplete": {}}

    for t in treinos:
        train_id = t.train_id
        is_complete = t.training_end is not None
        category = "Complete" if is_complete else "Incomplete"

        if train_id not in train_map[category]:
            train_map[category][train_id] = {
                "Name": t.train_name,
                "Expected_duration": t.expected_duration,
                "Exercises": {}
            }

        # Group exercises by name under each train
        exercises = train_map[category][train_id]["Exercises"]
        if t.exercise_name not in exercises:
            exercises[t.exercise_name] = {
                "exercise_name": t.exercise_name,
                "reps": [],
                "weight": [],
                "rest": []
            }

        exercises[t.exercise_name]["reps"].append(t.exercise_repetitions)
        exercises[t.exercise_name]["weight"].append(t.exercise_weight)
        exercises[t.exercise_name]["rest"].append(t.exercise_rest)

    # Convert exercise dicts to lists
    for category in train_map:
        for train_id in train_map[category]:
            exercises_dict = train_map[category][train_id]["Exercises"]
            train_map[category][train_id]["Exercises"] = list(exercises_dict.values())

    return train_map