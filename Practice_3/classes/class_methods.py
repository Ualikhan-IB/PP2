class Car:
    def __init__(self, make, model, year, color="White"):
        self.make = make
        self.model = model
        self.year = year
        self.color = color
        self.mileage = 0

    def drive(self, km):
        self.mileage += km
        return f"Drove {km} km. Total mileage: {self.mileage} km"

    def repaint(self, new_color):
        old_color = self.color
        self.color = new_color
        return f"Repainted from {old_color} to {new_color}"

    def __repr__(self):
        return f"{self.year} {self.color} {self.make} {self.model} ({self.mileage} km)"

my_car = Car("Toyota", "Corolla", 2022)
print(f"\n--- Car Object ---")
print(my_car)

my_car.year = 2023
print(my_car.repaint("Red"))
print(my_car.drive(150))
print(my_car)

my_car.owner = "Alice"
print(f"Owner added: {my_car.owner}")

del my_car.owner
print("Owner property deleted.")