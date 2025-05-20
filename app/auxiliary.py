from models import TrainExerciseView

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