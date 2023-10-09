import py_compile
import os
import zipfile
import shutil

LIB_PATH = "lib"

print("Package stdlib script")
print("LIB_PATH: {}".format(LIB_PATH))

for path, dirs, files in os.walk(LIB_PATH):
    for file in files:
        if not file.endswith(".pyc") and file.endswith(".py"):
            py_compile.compile(
                os.path.join(path, file), 
                os.path.join("tmp", path.removeprefix(os.path.join("lib", "python3.11")).lstrip("\\"), file.removesuffix(".py") + ".pyc")
            )

with zipfile.ZipFile("stdlib.zip", "w", zipfile.ZIP_STORED) as zipf:
    for path, dirs, files in os.walk("tmp"):
        for file in files:
            zipf.write(os.path.join(path, file), os.path.join(path.removeprefix("tmp").lstrip("\\"), file))

shutil.rmtree("tmp")

print("Package is done")