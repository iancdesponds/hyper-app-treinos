from models import TrainingAvailability

def format_train_return(treinos, results):
    # Agrupar os exercícios por train_id
    train_map = {}
    for t in treinos:
        train_id = t.train_id
        if train_id not in train_map:
            train_map[train_id] = []
        train_map[train_id].append(t)

    ordered_train_ids = list(train_map.keys())
    ordered_days = list(results.keys())

    for day, train_id in zip(ordered_days, ordered_train_ids):
        treinos_do_dia = train_map[train_id]
        if treinos_do_dia:
            results[day] = {
                "name": treinos_do_dia[0].train_name,
                "expected_duration": treinos_do_dia[0].expected_duration,
                "exercises": []
            }

            # Agrupar séries por nome de exercício
            grouped_exercises = {}
            for t in treinos_do_dia:
                name = t.exercise_name
                if name not in grouped_exercises:
                    grouped_exercises[name] = {
                        "exercise_name": name,
                        "reps": [],
                        "weight": [],
                        "rest": []
                    }
                grouped_exercises[name]["reps"].append(t.exercise_repetitions)
                grouped_exercises[name]["weight"].append(t.exercise_weight)
                grouped_exercises[name]["rest"].append(t.exercise_rest)

            results[day]["exercises"] = list(grouped_exercises.values())

    return results