class Shape:
    def __init__(self, color="black"):
        self.color = color

    def area(self):
        return 0

    def perimeter(self):
        return 0

    def describe(self):
        return (
            f"Shape    : {self.__class__.__name__}\n"
            f"Color    : {self.color}\n"
            f"Area     : {self.area():.2f}\n"
            f"Perimeter: {self.perimeter():.2f}"
        )

class Circle(Shape):
    import math

    def __init__(self, radius, color="black"):
        super().__init__(color)
        self.radius = radius

    def area(self):
        import math
        return math.pi * self.radius ** 2

    def perimeter(self):
        import math
        return 2 * math.pi * self.radius

class Rectangle(Shape):

    def __init__(self, width, height, color="black"):
        super().__init__(color)
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

class Triangle(Shape):

    def __init__(self, a, b, c, color="black"):
        super().__init__(color)
        self.a, self.b, self.c = a, b, c

    def area(self):
        import math
        s = (self.a + self.b + self.c) / 2
        return math.sqrt(s * (s-self.a) * (s-self.b) * (s-self.c))

    def perimeter(self):
        return self.a + self.b + self.c

shapes = [
    Circle(5, "red"),
    Rectangle(4, 7, "blue"),
    Triangle(3, 4, 5, "green"),
]

print("\n--- Method Overriding ---")
for shape in shapes:
    print(shape.describe())
    print()

print("Areas via polymorphism:")
for shape in shapes:
    print(f"  {shape.__class__.__name__}: {shape.area():.2f}")