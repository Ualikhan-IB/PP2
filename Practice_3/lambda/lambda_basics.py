def square_regular(x):
    return x ** 2

square_lambda = lambda x: x ** 2

print("\n--- Lambda Basics ---")
print(f"Regular function: {square_regular(5)}")
print(f"Lambda function:  {square_lambda(5)}")

add = lambda a, b: a + b
power = lambda base, exp: base ** exp

print(f"add(3, 4)      = {add(3, 4)}")
print(f"power(2, 10)   = {power(2, 10)}")