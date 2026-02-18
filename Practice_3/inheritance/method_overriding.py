class Animal:
    def __init__(self, name, species, age):
        self.name = name
        self.species = species
        self.age = age

    def eat(self, food):
        return f"{self.name} the {self.species} eats {food}."

class Flyable:
    def fly(self):
        return f"{self.name} is soaring through the sky! ✈️"

    def land(self):
        return f"{self.name} has landed safely."

class Swimmable:
    def swim(self):
        return f"{self.name} is swimming gracefully! 🌊"

    def dive(self):
        return f"{self.name} dives deep."

class Bird(Animal, Flyable):
    def __init__(self, name, age, can_fly=True):
        super().__init__(name, species="Bird", age=age)
        self.can_fly = can_fly

    def speak(self):
        return f"{self.name} tweets: Tweet tweet! 🐦"

class Duck(Animal, Flyable, Swimmable):
    def __init__(self, name, age):
        super().__init__(name, species="Duck", age=age)

    def speak(self):
        return f"{self.name} says: Quack quack! 🦆"

print("--- Multiple Inheritance ---")
eagle = Bird("Eagle", 4)
print(eagle.speak())
print(eagle.fly())
print(eagle.eat("fish"))

print()
donald = Duck("Donald", 3)
print(donald.speak())
print(donald.fly())
print(donald.swim())
print(donald.eat("bread"))

print(f"\nDuck MRO: {[cls.__name__ for cls in Duck.__mro__]}")