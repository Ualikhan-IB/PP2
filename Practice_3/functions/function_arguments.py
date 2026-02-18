def describe_pet(animal_type, pet_name):
    return f"I have a {animal_type} named {pet_name}."

print(describe_pet("dog", "Rex"))

print(describe_pet(pet_name="Whiskers", animal_type="cat"))
