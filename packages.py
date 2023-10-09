import py_compile
import os
import zipfile
import shutil
from . import ArchType, PlatformType

class AppPackage:
    def __init__(
        self, 
        arch: ArchType
    ):
        self.arch = arch

        app_package_path = os.path.join(os.getcwd(), "build", "intermediate", "app")
        os.makedirs(app_package_path, exist_ok=True)


    def package(self):
        assets_path = os.path.join(os.getcwd(), "build", "intermediate", "assets")

        result = self.__try_get_source_files__()
        if result is None:
            self.__scan_source_dir__()
            result = self.__try_get_source_files__()
        else:
            self.__scan_source_dir__()

        if len(result) > 0:
            if self.__copy_or_compile_sources__(result):
                print(f" Cooking {os.path.join(assets_path, 'app.zip')}")
                self.__archive_package__()
        else:
            print(f" Cooking {os.path.join(assets_path, 'app.zip')} was skipped")


    def __copy_or_compile_sources__(self, sources: list[str]) -> bool:
        app_package_path = os.path.join(os.getcwd(), "build", "intermediate", "app")
        src_dir = os.path.join(os.getcwd(), "src")
        lib_dir = os.path.join(os.getcwd(), "lib")

        result = True
        for item in sources:
            if item.endswith(".py"):
                try:
                    print(f" Build {os.path.join(src_dir, item)}")
                    py_compile.compile(os.path.join(src_dir, item), os.path.join(app_package_path, item.removesuffix(".py") + ".pyc"), doraise=True, quiet=1)
                except py_compile.PyCompileError as e:
                    print(f" Build failed!\n{e}")
                    result = False
                    break
            elif item.endswith(".so") or item.endswith(".dll") or item.endswith(".pyd"):
                os.makedirs(os.path.dirname(os.path.join(app_package_path, item)), exist_ok=True)
                shutil.copyfile(os.path.join(lib_dir, item), os.path.join(app_package_path, item))
                print(f" Copy {os.path.join(lib_dir, item)}")

        return result
    

    def __archive_package__(self):
        app_package_path = os.path.join(os.getcwd(), "build", "intermediate", "app")
        assets_path = os.path.join(os.getcwd(), "build", "intermediate", "assets")

        os.makedirs(assets_path, exist_ok=True)

        with zipfile.ZipFile(os.path.join(assets_path, "app.zip"), "w", zipfile.ZIP_STORED) as zipfp:
            with open(os.path.join(app_package_path, ".files"), "rt") as fp:
                while True:
                    line = fp.readline().strip('\n')
            
                    if line == None or line == '':
                        break

                    data = line.split(',')

                    file_path = data[0]

                    if file_path.endswith(".py"):
                        file_name = os.path.join(app_package_path, file_path.removesuffix(".py") + ".pyc")
                        arc_name = os.path.relpath(file_name, app_package_path)
                    elif file_path.endswith(".so") or file_path.endswith(".dll") or file_path.endswith(".pyd"):
                        file_name = os.path.join(app_package_path, file_path)
                        arc_name = os.path.join("modules", os.path.basename(file_name))
                    zipfp.write(file_name, arc_name)
    

    def __scan_source_dir__(self):
        app_package_path = os.path.join(os.getcwd(), "build", "intermediate", "app")
        src_dir = os.path.join(os.getcwd(), "src")
        lib_dir = os.path.join(os.getcwd(), "lib")

        with open(os.path.join(app_package_path, ".files"), "wt") as fp:
            for path, _, files in os.walk(src_dir):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.relpath(os.path.join(path, file), src_dir)
                        file_size = os.path.getsize(os.path.join(path, file))
                        file_mtime = os.path.getmtime(os.path.join(path, file))

                        fp.write(f"{file_path},{file_size},{file_mtime}\n")

            for path, _, files in os.walk(os.path.join(lib_dir, ArchType.name(self.arch))):
                for file in files:
                    if file.endswith(".so") or file.endswith(".dll") or file.endswith(".pyd"):
                        file_path = os.path.relpath(os.path.join(path, file), lib_dir)
                        file_size = os.path.getsize(os.path.join(path, file))
                        file_mtime = os.path.getmtime(os.path.join(path, file))

                        fp.write(f"{file_path},{file_size},{file_mtime}\n")

        
    def __try_get_source_files__(self) -> list[str] | None:
        output = []

        app_package_path = os.path.join(os.getcwd(), "build", "intermediate", "app")
        src_dir = os.path.join(os.getcwd(), "src")
        lib_dir = os.path.join(os.getcwd(), "lib")

        if os.path.exists(os.path.join(app_package_path, ".files")):
            with open(os.path.join(app_package_path, ".files"), "rt") as fp:
                while True:
                    line = fp.readline().strip('\n')
            
                    if line == None or line == '':
                        break

                    data = line.split(',')

                    file_path = data[0]
                    file_size = int(data[1])
                    file_mtime = float(data[2])

                    if file_path.endswith(".py"):
                        if os.path.exists(os.path.join(app_package_path, file_path.removesuffix(".py") + ".pyc")):
                            scan_size = os.path.getsize(os.path.join(src_dir, file_path))
                            scan_mtime = os.path.getmtime(os.path.join(src_dir, file_path))

                            if file_size != scan_size and file_mtime != scan_mtime:
                                output.append(file_path)
                        else:
                            output.append(file_path)

                    if file_path.endswith(".so") or file_path.endswith(".dll") or file_path.endswith(".pyd"):
                        if os.path.exists(os.path.join(app_package_path, file_path)):
                            scan_size = os.path.getsize(os.path.join(lib_dir, file_path))
                            scan_mtime = os.path.getmtime(os.path.join(lib_dir, file_path))

                            if file_size != scan_size and file_mtime != scan_mtime:
                                output.append(file_path)
                        else:
                            output.append(file_path)
            return output
        else:
            return None
        

class BootstrapPackage:
    def __init__(
        self,
        platform: PlatformType,
        arch: ArchType,
        py_version: str
    ):
        self.platform = platform
        self.arch = arch
        self.py_version = py_version

        bootstrap_package_path = os.path.join(os.getcwd(), "build", "intermediate", "bootstrap")
        os.makedirs(bootstrap_package_path, exist_ok=True)


    def package(self):
        assets_path = os.path.join(os.getcwd(), "build", "intermediate", "assets")
        os.makedirs(assets_path, exist_ok=True)

        if os.path.exists(os.path.join(assets_path, "bootstrap.zip")):
            print(f" Cooking {os.path.join(assets_path, 'bootstrap.zip')} was skipped")
            return

        result = self.__try_get_source_files__()
        if result is None:
            self.__scan_source_dir__()
            result = self.__try_get_source_files__()

        if self.__copy_or_compile_sources__(result):
            print(f" Cooking {os.path.join(assets_path, 'bootstrap.zip')}")
            self.__archive_package__()


    def __archive_package__(self):
        bootstrap_package_path = os.path.join(os.getcwd(), "build", "intermediate", "bootstrap")
        assets_path = os.path.join(os.getcwd(), "build", "intermediate", "assets")

        os.makedirs(assets_path, exist_ok=True)

        with zipfile.ZipFile(os.path.join(assets_path, "bootstrap.zip"), "w", zipfile.ZIP_STORED) as zipfp:
            with open(os.path.join(bootstrap_package_path, ".files"), "rt") as fp:
                while True:
                    line = fp.readline().strip('\n')
            
                    if line == None or line == '':
                        break

                    data = line.split(',')

                    file_path = data[0]

                    if file_path.endswith(".py"):
                        file_name = os.path.join(bootstrap_package_path, file_path.removesuffix(".py") + ".pyc")
                        arc_name = os.path.relpath(file_name, bootstrap_package_path)
                    elif file_path.endswith(".dll") or file_path.endswith(".zip") or file_path.endswith(".exe") or file_path.endswith(".so"):
                        file_name = os.path.join(bootstrap_package_path, file_path)
                        arc_name = os.path.basename(file_name)
                    zipfp.write(file_name, arc_name)


    def __scan_source_dir__(self):
        bootstrap_package_path = os.path.join(os.getcwd(), "build", "intermediate", "bootstrap")
        src_dir = os.path.join(os.path.dirname(__file__), "platforms", PlatformType.name(self.platform))
        lib_dir = os.path.join(os.getcwd(), "build", "intermediate", "deps", f"python-{self.py_version}", "bin")

        with open(os.path.join(bootstrap_package_path, ".files"), "wt") as fp:
            for path, _, files in os.walk(src_dir):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.relpath(os.path.join(path, file), src_dir)
                        file_size = os.path.getsize(os.path.join(path, file))
                        file_mtime = os.path.getmtime(os.path.join(path, file))

                        fp.write(f"{file_path},{file_size},{file_mtime}\n")

            for path, _, files in os.walk(os.path.join(lib_dir, ArchType.name(self.arch))):
                for file in files:
                    if file.endswith(".dll") or file.endswith(".zip") or file.endswith(".exe") or file.endswith(".so"):
                        file_path = os.path.relpath(os.path.join(path, file), lib_dir)
                        file_size = os.path.getsize(os.path.join(path, file))
                        file_mtime = os.path.getmtime(os.path.join(path, file))

                        fp.write(f"{file_path},{file_size},{file_mtime}\n")


    def __copy_or_compile_sources__(self, sources: list[str]) -> bool:
        bootstrap_package_path = os.path.join(os.getcwd(), "build", "intermediate", "bootstrap")
        src_dir = os.path.join(os.path.dirname(__file__), "platforms", PlatformType.name(self.platform))
        lib_dir = os.path.join(os.getcwd(), "build", "intermediate", "deps", f"python-{self.py_version}", "bin")

        result = True
        for item in sources:
            if item.endswith(".py"):
                try:
                    print(f" Build {os.path.join(src_dir, item)}")
                    py_compile.compile(os.path.join(src_dir, item), os.path.join(bootstrap_package_path, item.removesuffix(".py") + ".pyc"), doraise=True, quiet=1)
                except py_compile.PyCompileError as e:
                    print(f" Build failed!\n{e}")
                    result = False
                    break
            elif item.endswith(".dll") or item.endswith(".zip") or item.endswith(".exe") or item.endswith(".so"):
                os.makedirs(os.path.dirname(os.path.join(bootstrap_package_path, item)), exist_ok=True)
                shutil.copyfile(os.path.join(lib_dir, item), os.path.join(bootstrap_package_path, item))
                print(f" Copy {os.path.join(lib_dir, item)}")

        return result
    

    def __try_get_source_files__(self) -> list[str] | None:
        output = []

        bootstrap_package_path = os.path.join(os.getcwd(), "build", "intermediate", "bootstrap")
        src_dir = os.path.join(os.path.dirname(__file__), "platforms", PlatformType.name(self.platform))
        lib_dir = os.path.join(os.getcwd(), "build", "intermediate", "deps", f"python-{self.py_version}", "bin")

        if os.path.exists(os.path.join(bootstrap_package_path, ".files")):
            with open(os.path.join(bootstrap_package_path, ".files"), "rt") as fp:
                while True:
                    line = fp.readline().strip('\n')
            
                    if line == None or line == '':
                        break

                    data = line.split(',')

                    file_path = data[0]
                    file_size = int(data[1])
                    file_mtime = float(data[2])

                    if file_path.endswith(".py"):
                        if os.path.exists(os.path.join(bootstrap_package_path, file_path.removesuffix(".py") + ".pyc")):
                            scan_size = os.path.getsize(os.path.join(src_dir, file_path))
                            scan_mtime = os.path.getmtime(os.path.join(src_dir, file_path))

                            if file_size != scan_size and file_mtime != scan_mtime:
                                output.append(file_path)
                        else:
                            output.append(file_path)

                    if file_path.endswith(".dll") or file_path.endswith(".zip") or file_path.endswith(".exe") or file_path.endswith(".so"):
                        if os.path.exists(os.path.join(bootstrap_package_path, file_path)):
                            scan_size = os.path.getsize(os.path.join(lib_dir, file_path))
                            scan_mtime = os.path.getmtime(os.path.join(lib_dir, file_path))

                            if file_size != scan_size and file_mtime != scan_mtime:
                                output.append(file_path)
                        else:
                            output.append(file_path)
            return output
        else:
            return None
