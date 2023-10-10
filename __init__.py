import zipfile
import os
import shutil
from io import StringIO
import py_compile

class ArchType:
    ARM64 = 0
    ARM = 1
    X64 = 2
    X86 = 3

    def name(type) -> str:
        match type:
            case ArchType.ARM64:
                return "arm64-v8a"
            case ArchType.ARM:
                return "armeabi-v7a"
            case ArchType.X64:
                return "x86_64"
            case ArchType.X86:
                return "x86"
        

class PlatformType:
    Windows = 0
    Linux = 1
    Android = 2

    def name(type) -> str:
        match type:
            case PlatformType.Windows:
                return "win32"
            case PlatformType.Linux:
                return "linux"
            case PlatformType.Android:
                return "android"
            

class BuildPlatform:
    def __init__(self, platform: PlatformType):
        self.platform = platform
        self.arch = None


    def configure(self, arch: ArchType):
        self.arch = arch

    
    def build(self):
        pass


class Library:
    def __init__(
        self,
        name: str,
        platform: PlatformType,
        version: str
    ):
        self.name = name
        self.platform = platform
        self.version = version

        deps_path = os.path.join(os.getcwd(), "build", "intermediate", "deps")
        os.makedirs(deps_path, exist_ok=True)
        
        
    def unpack(self):
        if os.path.exists(os.path.join(os.getcwd(), "build", "intermediate", "deps", f"{self.name}-{self.version}")):
            return

        print(f" Unpack {self.name}-{self.version}-{PlatformType.name(self.platform)}.zip")

        with zipfile.ZipFile(os.path.join(os.path.dirname(__file__), "deps", f"{self.name}-{self.version}-{PlatformType.name(self.platform)}.zip"), "r") as zipfp:
            zipfp.extractall(os.path.join(os.getcwd(), "build", "intermediate", "deps", f"{self.name}-{self.version}"))


class Package:
    def __init__(
        self,
        src_path: str,
        output_path: str
    ):
        self.src_path = src_path
        self.output_path = output_path

        
    def package(self):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        print(f" Pack {self.src_path}")

        with zipfile.ZipFile(os.path.join(self.output_path), "w", zipfile.ZIP_STORED) as zipfp:
            with open(os.path.join(self.src_path, ".sources"), "rt") as fp:
                while True:
                    line = fp.readline().strip('\n')
            
                    if line == None or line == '':
                        break

                    data = line.split(',')

                    file_path = data[0]

                    zipfp.write(os.path.join(self.src_path, file_path.removesuffix(".py") + ".pyc"), os.path.relpath(file_path, self.src_path))
            
            with open(os.path.join(self.src_path, ".binaries"), "rt") as fp:
                while True:
                    line = fp.readline().strip('\n')
            
                    if line == None or line == '':
                        break

                    data = line.split(',')

                    file_path = data[0]

                    if file_path.endswith('.so') or file_path.endswith('.pyd') or file_path.endswith('.dll'):
                        arc_name = os.path.join("modules", os.path.basename(file_path))
                    else:
                        arc_name = os.path.relpath(file_path, self.src_path)
                    zipfp.write(os.path.join(self.src_path, file_path), arc_name)


def compile_sources(src_path: str, out_path: str, cache_path: str, out_cache: StringIO) -> int | bool:
    os.makedirs(out_path, exist_ok=True)

    count = 0

    def get_sources_using_cache_file() -> list[str]:
        out = []

        with open(os.path.join(out_path, ".sources"), "rt") as fp:
            while True:
                line = fp.readline().strip('\n')
            
                if line == None or line == '':
                    break

                data = line.split(',')

                file_path = data[0]
                file_size = int(data[1])
                file_mtime = float(data[2])

                if file_path.endswith('.py'):
                    scan_size = os.path.getsize(os.path.join(src_path, file_path))
                    scan_mtime = os.path.getmtime(os.path.join(src_path, file_path))

                    if file_size != scan_size and file_mtime != scan_mtime:
                        out.append(file_path)
        return out

    def get_sources_without_cache_file() -> list[str]:
        out = []

        for path, _, files in os.walk(src_path):
            for file in files:
                if file.endswith('.py'):
                    out.append(os.path.relpath(os.path.join(path, file), src_path))
        return out

    if cache_path:
        sources = get_sources_using_cache_file()
    else:
        sources = get_sources_without_cache_file()

    result = True
    for source in sources:
        if source.endswith(".py"):
            try:
                print(f" Build {os.path.join(src_path, source)}")
                py_compile.compile(
                    os.path.join(src_path, source), 
                    os.path.join(out_path, source.removesuffix(".py") + ".pyc"), 
                    doraise=True, 
                    quiet=1
                )
                count += 1
            except py_compile.PyCompileError as e:
                print(f" Build failed!\n{e}")
                result = False
                break

    if result:
        for path, _, files in os.walk(src_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.relpath(os.path.join(path, file), src_path)
                    file_size = os.path.getsize(os.path.join(path, file))
                    file_mtime = os.path.getmtime(os.path.join(path, file))

                    out_cache.write(f"{file_path},{file_size},{file_mtime}\n")
        return count
    else:
        return result


def copy_binaries(src_path: str, out_path: str, cache_path: str, out_cache: StringIO) -> int:
    os.makedirs(out_path, exist_ok=True)

    count = 0

    def get_binaries_using_cache_file() -> list[str]:
        out = []

        with open(os.path.join(out_path, ".binaries"), "rt") as fp:
            while True:
                line = fp.readline().strip('\n')
            
                if line == None or line == '':
                    break

                data = line.split(',')

                file_path = data[0]
                file_size = int(data[1])
                file_mtime = float(data[2])

                if not (file_path.endswith('.py') or file_path.endswith('.pyi') or file_path.endswith('.pyc')):
                    scan_size = os.path.getsize(os.path.join(src_path, file_path))
                    scan_mtime = os.path.getmtime(os.path.join(src_path, file_path))

                    if file_size != scan_size and file_mtime != scan_mtime:
                        out.append(file_path)
        return out

    def get_binaries_without_cache_file() -> list[str]:
        out = []

        for path, _, files in os.walk(src_path):
            for file in files:
                if not (file.endswith('.py') or file.endswith('.pyi') or file.endswith('.pyc')):
                    out.append(os.path.relpath(os.path.join(path, file), src_path))
        return out

    if cache_path:
        binaries = get_binaries_using_cache_file()
    else:
        binaries = get_binaries_without_cache_file()

    for binary in binaries:
        if not (binary.endswith('.py') or binary.endswith('.pyi') or binary.endswith('.pyc')):
            os.makedirs(os.path.dirname(os.path.join(out_path, binary)), exist_ok=True)
            shutil.copyfile(os.path.join(src_path, binary), os.path.join(out_path, binary))
            print(f" Copy {os.path.join(src_path, binary)}")
            count += 1

    for path, _, files in os.walk(src_path):
        for file in files:
            if not (file.endswith('.py') or file.endswith('.pyi') or file.endswith('.pyc')):
                file_path = os.path.relpath(os.path.join(path, file), src_path)
                file_size = os.path.getsize(os.path.join(path, file))
                file_mtime = os.path.getmtime(os.path.join(path, file))

                out_cache.write(f"{file_path},{file_size},{file_mtime}\n")

    return count
