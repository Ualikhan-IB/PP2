import os

os.mkdir("my_folder")
os.makedirs("parent/child/grandchild", exist_ok=True)

for item in os.listdir("."):
    print(item)

for item in os.listdir("."):
    print(os.path.join(os.getcwd(), item))
