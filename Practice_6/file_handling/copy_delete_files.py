import shutil
import os

shutil.copy("output.txt", "output_copy.txt")
os.rename("output_copy.txt", "renamed.txt")

if os.path.exists("renamed.txt"):
    os.remove("renamed.txt")
