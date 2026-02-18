students = [
    {"name": "Alice",   "grade": 88, "age": 22},
    {"name": "Charlie", "grade": 72, "age": 25},
    {"name": "Bob",     "grade": 95, "age": 20},
    {"name": "Diana",   "grade": 72, "age": 23},
]

by_grade = sorted(students, key=lambda s: s["grade"])

by_grade_desc = sorted(students, key=lambda s: (-s["grade"], s["name"]))

print("\n--- sorted() with Lambda ---")
print("By grade (ascending):")
for s in by_grade:
    print(f"  {s['name']:10} Grade: {s['grade']}")

print("By grade (descending), name as tiebreaker:")
for s in by_grade_desc:
    print(f"  {s['name']:10} Grade: {s['grade']}")

fruits = ["banana", "apple", "cherry", "date", "fig"]
by_last_char = sorted(fruits, key=lambda f: f[-1])
print(f"\nFruits sorted by last character: {by_last_char}")
