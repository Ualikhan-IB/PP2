class Employee:
    company = "Tech Corp"
    employee_count = 0

    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
        Employee.employee_count += 1
        self.employee_id = Employee.employee_count

    def give_raise(self, percent):
        self.salary *= (1 + percent / 100)
        return f"{self.name}'s new salary: {self.salary:.2f}"

    def __str__(self):
        return f"Employee #{self.employee_id}: {self.name} | Salary: {self.salary:.2f}"

emp1 = Employee("Alice", 60000)
emp2 = Employee("Bob", 75000)
emp3 = Employee("Charlie", 55000)

print("\n--- Class vs Instance Variables ---")
print(emp1)
print(emp2)
print(emp3)
print(f"Total employees (class variable): {Employee.employee_count}")

emp1.give_raise(10)
print(f"\nAfter raise -> {emp1}")
print(f"Bob unchanged -> {emp2}")

Employee.company = "Mega Tech Corp"
print(f"\nCompany for emp1: {emp1.company}")
print(f"Company for emp2: {emp2.company}")