import shutil
import os

with open("test.txt", "w") as f:
    f.write("test content")

os.makedirs("my_folder", exist_ok=True)
shutil.move("test.txt", "my_folder/test.txt")
