all_numbers = range(1, 21)

even_numbers = list(filter(lambda n: n % 2 == 0, all_numbers))

fizzbuzz_numbers = list(filter(lambda n: n % 3 == 0 or n % 5 == 0, all_numbers))

print("\n--- filter() with Lambda ---")
print(f"Even numbers (1-20):          {even_numbers}")
print(f"Divisible by 3 or 5 (1-20):  {fizzbuzz_numbers}")

words = ["apple", "banana", "fig", "kiwi", "strawberry", "pea"]
long_words = list(filter(lambda w: len(w) > 4, words))
print(f"Words longer than 4 chars:   {long_words}")