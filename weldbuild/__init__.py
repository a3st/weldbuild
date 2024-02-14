import zipfile
import os
import shutil
import py_compile
import datetime

Version = tuple[int, int, int]


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
        self.site_packages = []

    def configure(self, arch: ArchType):
        self.arch = arch

        clean = True

        if os.path.exists(
            os.path.join(os.getcwd(), "build", "intermediate", ".configure")
        ):
            with open(
                os.path.join(os.getcwd(), "build", "intermediate", ".configure"), "rt"
            ) as fp:
                data = fp.read()
                _, value = data.split("=")

                if value == ArchType.name(arch):
                    clean = False

        if clean:
            shutil.rmtree(os.path.join(os.getcwd(), "build"), ignore_errors=True)

            os.makedirs(
                os.path.join(os.getcwd(), "build", "intermediate"), exist_ok=True
            )

            with open(
                os.path.join(os.getcwd(), "build", "intermediate", ".configure"), "wt"
            ) as fp:
                fp.write(f"ARCH={ArchType.name(arch)}")

    def add_site_packages(self, packages: list[str]):
        self.site_packages.extend(packages)

    def build(self):
        pass


class Library:
    def __init__(self, name: str, platform: PlatformType, version: str):
        self.name = name
        self.platform = platform
        self.version = version

        self.out_path = os.path.join(os.getcwd(), "build", "intermediate", "deps")
        os.makedirs(self.out_path, exist_ok=True)

    def path(self) -> str:
        return f"{self.name}-{self.version}"

    def unpack(self):
        if os.path.exists(os.path.join(self.out_path, self.path())):
            return

        print(f" Unpack {self.path()}-{PlatformType.name(self.platform)}.zip")

        with zipfile.ZipFile(
            os.path.join(
                os.path.dirname(__file__),
                "deps",
                f"{self.path()}-{PlatformType.name(self.platform)}.zip",
            ),
            "r",
        ) as zipfp:
            zipfp.extractall(os.path.join(self.out_path, self.path()))


def archive_package(src_path: str, version: Version, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f" Pack {src_path}")

    # Calculate version and build timestamp
    version_string = ".".join(map(str, version))
    version_timestamp = str(datetime.datetime.now().timestamp().as_integer_ratio()[1])

    # Create .VERSION file - VERSION_STRING.VERSION_TIMESTAMP
    with open(os.path.join(src_path, ".VERSION"), "wt") as fp:
        fp.write(f"{version_string}.{version_timestamp}")

    # Create ZIP archive
    with zipfile.ZipFile(os.path.join(output_path), "w", zipfile.ZIP_STORED) as zipfp:
        for path, _, files in os.walk(src_path):
            for file in files:
                zipfp.write(
                    os.path.join(path, file),
                    os.path.relpath(os.path.join(path, file), src_path),
                )

    return f"{version_string}.{version_timestamp}"


def copy_compile(src_path: str, out_path: str, dir_name: str = "") -> int:
    def get_sources() -> list[str]:
        out = []

        for path, _, files in os.walk(src_path):
            for file in files:
                if not file.endswith(".pyc"):
                    out.append(os.path.join(path, file))
        return out

    def get_database() -> dict:
        out = {}

        with open(
            os.path.join(os.getcwd(), "build", "intermediate", ".sources"), "rt"
        ) as fp:
            while True:
                line = fp.readline().strip("\n")

                if line == None or line == "":
                    break

                data = line.split(",")

                file_path = data[0]
                file_size = int(data[1])
                file_mtime = float(data[2])

                out[file_path] = (file_size, file_mtime)
        return out

    def filter_sources(sources: list[str], database: dict) -> list[str]:
        out = []

        for source in sources:
            value = database.get(source)

            scan_size = os.path.getsize(source)
            scan_mtime = os.path.getmtime(source)

            if value is not None:
                if value[0] != scan_size and value[1] != scan_mtime:
                    out.append(source)
            else:
                database[source] = (scan_size, scan_mtime)
                out.append(source)
        return out

    def save_database_to_file(database: dict):
        with open(
            os.path.join(os.getcwd(), "build", "intermediate", ".sources"), "wt"
        ) as fp:
            for key, value in database.items():
                fp.write(f"{key},{value[0]},{value[1]}\n")

    os.makedirs(out_path, exist_ok=True)
    size = 0

    # First, we are need get sources files
    sources = get_sources()

    # If out_path already has .sources - text file
    if os.path.exists(os.path.join(os.getcwd(), "build", "intermediate", ".sources")):
        # Get database from .sources - text file
        database = get_database()
    else:
        database = {}
    # We are need filter it for speed optimizations
    sources = filter_sources(sources, database)

    # Iterate over sources. If it is .py - compile, .etc - copy as binary file
    for source in sources:
        if source.endswith(".py"):
            try:
                print(f" Build {source}")
                py_compile.compile(
                    source,
                    os.path.join(
                        out_path,
                        dir_name,
                        os.path.relpath(source.removesuffix(".py") + ".pyc", src_path),
                    ),
                    doraise=True,
                    quiet=1,
                )
                size += 1
            except py_compile.PyCompileError as e:
                raise RuntimeError(f" Build failed!\n{e}")
        else:
            print(f" Copy {source}")
            os.makedirs(
                os.path.dirname(
                    os.path.join(out_path, dir_name, os.path.relpath(source, src_path))
                ),
                exist_ok=True,
            )
            shutil.copyfile(
                source,
                os.path.join(out_path, dir_name, os.path.relpath(source, src_path)),
            )
            size += 1

    # Rewrite database if files has been changed
    if size > 0:
        save_database_to_file(database)
    return size
