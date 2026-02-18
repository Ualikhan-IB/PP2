class Animal:
    def __init__(self, name, species, age):
        self.name = name
        self.species = species
        self.age = age
        self.is_alive = True

    def eat(self, food):
        return f"{self.name} the {self.species} eats {food}."

    def breathe(self):
        return f"{self.name} breathes air."

    def describe(self):
        return f"{self.name} | Species: {self.species} | Age: {self.age}"

class Dog(Animal):
    def __init__(self, name, age, breed):
        super().__init__(name, species="Dog", age=age)
        self.breed = breed
        self.tricks = []

    def learn_trick(self, trick):
        self.tricks.append(trick)
        return f"{self.name} learned '{trick}'!"

    def perform(self):
        if self.tricks:
            return f"{self.name} performs: {', '.join(self.tricks)}"
        return f"{self.name} doesn't know any tricks yet."

    def describe(self):
        base = super().describe()
        return f"{base} | Breed: {self.breed}"

class Cat(Animal):
    def __init__(self, name, age, indoor=True):
        super().__init__(name, species="Cat", age=age)
        self.indoor = indoor

    def purr(self):
        return f"{self.name} purrs contentedly... 🐱"

    def describe(self):
        location = "indoor" if self.indoor else "outdoor"
        return f"{super().describe()} | {location.capitalize()} cat"

dog = Dog("Rex", 3, "Labrador")
cat = Cat("Luna", 5)

print("\n--- Inheritance Example ---")
print(dog.describe())
print(dog.eat("kibble"))
print(dog.breathe())
print(dog.learn_trick("Sit"))
print(dog.learn_trick("Shake"))
print(dog.perform())

print()
print(cat.describe())
print(cat.purr())
print(cat.eat("tuna"))