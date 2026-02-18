def calculate_total(*prices, discount=0, currency="USD"):
    subtotal = sum(prices)
    final_total = subtotal - discount
    return f"Total ({currency}): {final_total:.2f} (saved {discount:.2f})"

print(calculate_total(19.99, 5.49, 12.00))
print(calculate_total(100.00, 250.00, 75.50, discount=30, currency="EUR"))

def display_profile(**info):
    print("--- User Profile ---")
    for key, value in info.items():
        print(f"  {key.capitalize()}: {value}")

display_profile(name="Alice", age=30, city="New York", job="Engineer")