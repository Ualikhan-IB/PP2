temperatures_celsius = [0, 20, 37, 100, -10]

temperatures_fahrenheit = list(map(lambda c: (c * 9/5) + 32, temperatures_celsius))

print("\n--- map() with Lambda ---")
print(f"Celsius:    {temperatures_celsius}")
print(f"Fahrenheit: {temperatures_fahrenheit}")

numbers = [1, 2, 3, 4, 5]
doubled = list(map(lambda n: n * 2, numbers))
print(f"Original: {numbers}  →  Doubled: {doubled}")