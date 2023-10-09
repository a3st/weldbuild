import os
import zipfile
import shutil

LIB_DYN_PATH = "lib-dynload"

print("Package stdlib script")
print("LIB_DYN_PATH: {}".format(LIB_DYN_PATH))

shutil.copytree(LIB_DYN_PATH, "tmp")

for path, dirs, files in os.walk("tmp"):
    for file in files:
        if file.endswith(".so"):
            os.rename(os.path.join(path, file), os.path.join(path, file.removesuffix(".cpython-311.so") + ".so"))

with zipfile.ZipFile("modules.zip", "w", zipfile.ZIP_STORED) as zipf:
    for path, dirs, files in os.walk("tmp"):
        for file in files:
            zipf.write(os.path.join(path, file), os.path.join(path.removeprefix("tmp").lstrip("\\"), file))

shutil.rmtree("tmp")

print("Package is done")