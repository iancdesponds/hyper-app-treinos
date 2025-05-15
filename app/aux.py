from models import TrainingAvailability

def format_train_return(treinos, results):
    used_ids = set()
    for treino in treinos:
        for day in results:
            if results[day] == {} and getattr(treino, "train_id") not in used_ids:
                results[day] = {
                    "name": getattr(treino, "train_name"),
                    "expected_duration": getattr(treino, "expected_duration"),
                    "exercises": []
                }
                results[day]["exercises"].append(
                    {
                        "exercise_name": getattr(treino, "exercise_name"),
                        "reps": getattr(treino, "exercise_repetitions"),
                        "weight": getattr(treino, "exercise_weight"),
                        "rest": getattr(treino, "exercise_rest")
                    }
                )
                used_ids.add(getattr(treino, "train_id"))
                break
            else:
                if "exercises" in results[day]:
                    results[day]["exercises"].append(
                        {
                            "exercise_name": getattr(treino, "exercise_name"),
                            "reps": getattr(treino, "exercise_repetitions"),
                            "weight": getattr(treino, "exercise_weight"),
                            "rest": getattr(treino, "exercise_rest")
                        }
                    )
    return results