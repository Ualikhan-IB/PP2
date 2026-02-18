class ShoppingCart:
    def __init__(self, customer_name):
        self.customer = customer_name
        self.items = {}

    def add_item(self, name, price, quantity=1):
        if name in self.items:
            self.items[name] = (price, self.items[name][1] + quantity)
        else:
            self.items[name] = (price, quantity)

    def remove_item(self, name):
        if name in self.items:
            del self.items[name]
            return f"Removed '{name}' from cart."
        return f"'{name}' not in cart."

    def get_total(self):
        return sum(price * qty for price, qty in self.items.values())

    def __str__(self):
        lines = [f"🛒 {self.customer}'s Cart:"]
        for name, (price, qty) in self.items.items():
            lines.append(f"  {name:<15} x{qty}  @ {price:.2f} = {price*qty:.2f}")
        lines.append(f"  {'TOTAL':<15}        = {self.get_total():.2f}")
        return "\n".join(lines)

    def __len__(self):
        return sum(qty for _, qty in self.items.values())

cart = ShoppingCart("Alice")
cart.add_item("Apple", 0.99, 4)
cart.add_item("Milk", 2.49)
cart.add_item("Bread", 3.99)
cart.add_item("Apple", 0.99, 2)

print(f"\n{cart}")
print(f"Total items in cart: {len(cart)}")
print(cart.remove_item("Milk"))
print(f"\nAfter removal:\n{cart}")