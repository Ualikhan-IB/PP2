class Father:
    def coding(self):
        return "Father умеет программировать"

class Mother:
    def cooking(self):
        return "Mother умеет готовить"

class Child(Father, Mother):
    def skills(self):
        return f"{self.coding()} и {self.cooking()}"


child = Child()

print(child.coding())   
print(child.cooking())   
print(child.skills())    
