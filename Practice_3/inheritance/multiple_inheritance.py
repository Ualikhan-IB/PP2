from abc import ABC, abstractmethod

class Vehicle(ABC):
    def __init__(self, brand, model, year):
        self.brand = brand
        self.model = model
        self.year = year
        self.is_running = False

    @abstractmethod
    def start_engine(self):
        pass

    @abstractmethod
    def fuel_type(self):
        pass

    def stop_engine(self):
        self.is_running = False
        return f"{self.brand} {self.model} engine stopped."

    def info(self):
        status = "Running" if self.is_running else "Off"
        return (
            f"{self.year} {self.brand} {self.model} | "
            f"Fuel: {self.fuel_type()} | Status: {status}"
        )

class ElectricCar(Vehicle):
    def __init__(self, brand, model, year, battery_kwh):
        super().__init__(brand, model, year)
        self.battery_kwh = battery_kwh
        self.charge = 100

    def start_engine(self):
        self.is_running = True
        return f"{self.brand} {self.model} motor activated silently. 🔋"

    def fuel_type(self):
        return "Electric"

    def charge_battery(self):
        self.charge = 100
        return f"Battery charged to 100%! ({self.battery_kwh} kWh)"

class GasCar(Vehicle):
    def __init__(self, brand, model, year, engine_cc):
        super().__init__(brand, model, year)
        self.engine_cc = engine_cc

    def start_engine(self):
        self.is_running = True
        return f"{self.brand} {self.model} engine roars to life! 🔑 ({self.engine_cc}cc)"

    def fuel_type(self):
        return "Gasoline"

class Motorcycle(Vehicle):
    def __init__(self, brand, model, year, style="Sport"):
        super().__init__(brand, model, year)
        self.style = style

    def start_engine(self):
        self.is_running = True
        return f"{self.brand} {self.model} {self.style} bike roars! 🏍️"

    def fuel_type(self):
        return "Gasoline"

print("\n--- Abstract Base Classes (Task 4 - Advanced) ---")

tesla = ElectricCar("Tesla", "Model 3", 2023, battery_kwh=75)
honda = GasCar("Honda", "Civic", 2022, engine_cc=1500)
yamaha = Motorcycle("Yamaha", "R1", 2023, "Sport")

vehicles = [tesla, honda, yamaha]

for vehicle in vehicles:
    print(vehicle.start_engine())
    print(vehicle.info())
    print(vehicle.stop_engine())
    print()

print("All vehicles fuel types (polymorphism):")
for vehicle in vehicles:
    print(f"  {vehicle.brand} {vehicle.model}: {vehicle.fuel_type()}")
