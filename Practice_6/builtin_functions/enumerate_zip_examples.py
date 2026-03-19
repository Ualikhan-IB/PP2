fruits = ["apple", "banana", "cherry"]
prices = [1.2, 0.5, 2.0]

for i, fruit in enumerate(fruits):
    print(i, fruit)

for i, fruit in enumerate(fruits, start=1):
    print(i, fruit)

for fruit, price in zip(fruits, prices):
    print(fruit, price)

print(dict(zip(fruits, prices)))
