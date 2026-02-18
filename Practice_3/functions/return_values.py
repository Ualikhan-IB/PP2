def analyze_scores(scores):
    if not scores:
        return {"error": "No scores provided"}

    result = {
        "count":   len(scores),
        "average": sum(scores) / len(scores),
        "highest": max(scores),
        "lowest":  min(scores),
        "passed":  [s for s in scores if s >= 50],
    }
    return result

student_scores = [72, 85, 91, 45, 63, 55, 88]
analysis = analyze_scores(student_scores)

print("\n--- Score Analysis ---")
for key, value in analysis.items():
    print(f"  {key}: {value}")