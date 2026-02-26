def squares(n):
    for i in range(1, n + 1):
        yield i * i

n = int(input("Enter N: "))
for val in squares(n):
    print(val)
