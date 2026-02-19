class Animal:
    def speak(self):
        return "Animal издаёт звук"

class Dog(Animal):
    def speak(self):
        return "Dog говорит: Woof!"

class Cat(Animal):
    def speak(self):
        return "Cat говорит: Meow!"


animal = Animal()
dog = Dog()
cat = Cat()

print(animal.speak()) 
print(dog.speak())    
print(cat.speak())     