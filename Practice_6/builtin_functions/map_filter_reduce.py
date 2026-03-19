from functools import reduce

numbers = [1, 2, 3, 4, 5]

squared = list(map(lambda x: x ** 2, numbers))
print(squared)

evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)

total = reduce(lambda x, y: x + y, numbers)
print(total)
