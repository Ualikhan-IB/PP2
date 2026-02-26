def divisible_by_3_and_4(n):
    for i in range(0, n + 1):
        if i % 12 == 0:
            yield i

n = int(input("Enter N: "))
print(' '.join(str(val) for val in divisible_by_3_and_4(n)))
