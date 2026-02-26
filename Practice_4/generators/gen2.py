def even_numbers(n):
    for i in range(0, n + 1, 2):
        yield i

n = int(input("Enter N: "))
print(','.join(str(val) for val in even_numbers(n)))
