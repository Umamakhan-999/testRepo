from ortools.sat.python import cp_model

def solve_exam_schedule():
    subjects = ["Math", "Physics", "AI", "OS", "DB"]
    slots = range(1, 7)
    days = {1: [1, 2], 2: [3, 4], 3: [5, 6]}

    model = cp_model.CpModel()
    exam = {s: model.NewIntVar(1, 6, s) for s in subjects}
    b = {}
    for s in subjects:
        for t in slots:
            b[s, t] = model.NewBoolVar(f"{s}_{t}")
            model.Add(exam[s] == t).OnlyEnforceIf(b[s, t])
            model.Add(exam[s] != t).OnlyEnforceIf(b[s, t].Not())
        model.AddExactlyOne(b[s, t] for t in slots)

    model.Add(exam["Math"] != exam["Physics"])
    model.Add(exam["AI"] != exam["OS"])
    model.Add(exam["OS"] != exam["DB"])

    for d, d_slots in days.items():
        model.Add(sum(b[s, t] for s in subjects for t in d_slots) <= 2)

    for t in slots:
        model.Add(sum(b[s, t] for s in subjects) <= 2)

    diff = model.NewIntVar(-5, 5, "diff")
    absdiff = model.NewIntVar(0, 5, "absdiff")
    model.Add(diff == exam["AI"] - exam["OS"])
    model.AddAbsEquality(absdiff, diff)
    model.Add(absdiff >= 2)

    # Ordering: Math before DB
    model.Add(exam["Math"] < exam["DB"])

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        schedule = {s: solver.Value(exam[s]) for s in subjects}
        for s, t in schedule.items():
            day = (t - 1) // 2 + 1
            print(f"{s}: Slot {t} (Day {day})")
        return schedule
    else:
        print("No valid schedule found.")
        return None

solve_exam_schedule()