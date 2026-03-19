with open("output.txt", "w") as f:
    f.write("First line\n")
    f.write("Second line\n")

with open("output.txt", "a") as f:
    f.write("Third line\n")

lines = ["Apple\n", "Banana\n", "Cherry\n"]
with open("fruits.txt", "w") as f:
    f.writelines(lines)
