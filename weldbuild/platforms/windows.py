import os
import shutil
import subprocess
import json
import site
from .. import (
    BuildPlatform,
    ArchType,
    PlatformType,
    Version,
    archive_package,
    copy_compile,
)
from ..deps import Python, LibZip, ZLib
from ..utils.png2ico import ICOParser
from ..utils.cmake import CMake, CMakeTargetType, cmake_path


class WindowsBuild(BuildPlatform):
    def __init__(
        self,
        app_version: Version,
        app_name: str,
        app_icons: dict,
        app_console: bool,
        py_version: str = "3.11.5",
    ):
        BuildPlatform.__init__(self, PlatformType.Windows)
        self.py_version = py_version

        self.app_version = app_version
        self.app_name = app_name
        self.app_icons = app_icons
        self.app_console = app_console

        self.BUILD_VERSION = None

    def configure(self, arch: ArchType):
        BuildPlatform.configure(self, arch)

        self.__unpack_dependicies__()
        self.__make_icon__()
        self.__package__()
        self.__create_project__(arch)

        print(" Done!")

    def build(self):
        BuildPlatform.build(self)

        try:
            output = subprocess.check_output(
                [
                    os.path.join(
                        "C:",
                        "Program Files (x86)",
                        "Microsoft Visual Studio",
                        "Installer",
                        "vswhere.exe",
                    ),
                    "-products",
                    "*",
                    "-format",
                    "json",
                    "-utf8",
                    "-prerelease",
                    "-requires",
                    "Microsoft.Component.MSBuild",
                ]
            )

            data = json.loads(output)
            cmd_path = os.path.join(
                data[0]["installationPath"], "Common7", "Tools", "VsDevCmd.bat"
            )
        except FileNotFoundError:
            print("Error: vswhere.exe not found")

        try:
            match self.arch:
                case ArchType.X64:
                    ARCH = "x64"
                case ArchType.X86:
                    ARCH = "Win32"
                case ArchType.ARM:
                    ARCH = "ARM"
                case ArchType.ARM64:
                    ARCH = "ARM64"

            subprocess.call(
                [cmd_path, "&", "cmake", "-B", "build", "-A", ARCH],
                cwd=os.path.join(os.getcwd(), "build", "generated"),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            subprocess.check_call(
                [cmd_path, "&", "cmake", "--build", "build", "--config", "Release"],
                cwd=os.path.join(os.getcwd(), "build", "generated"),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            os.makedirs(os.path.join(os.getcwd(), "dist"), exist_ok=True)

            shutil.copyfile(
                os.path.join(
                    os.getcwd(), "build", "generated", "build", "Release", "main.exe"
                ),
                os.path.join(os.getcwd(), "dist", "main.exe"),
            )

            print(f" Out: {os.path.join(os.getcwd(), 'dist', 'main.exe')}")

        except FileNotFoundError as e:
            print("Error: VsDevCmd.bat not found")

        except subprocess.CalledProcessError:
            print("Error: Build exit with error")

    def __make_icon__(self):
        os.makedirs(
            os.path.join(os.getcwd(), "build", "intermediate", "assets"), exist_ok=True
        )
        ICOParser(self.app_icons.values()).save_to_file(
            os.path.join(os.getcwd(), "build", "intermediate", "assets", "app.ico")
        )

    def __unpack_dependicies__(self):
        print(" Checking missing dependicies...")

        Python(self.platform, self.py_version).unpack()
        LibZip(self.platform).unpack()
        ZLib(self.platform).unpack()

    def __package__(self):
        print(" Cooking python scripts...")

        archive_size = 0

        src_path = os.path.join(os.getcwd(), "src")
        out_path = os.path.join(
            os.getcwd(), "build", "intermediate", "app", "site-packages"
        )

        try:
            size = copy_compile(src_path, out_path, "__app__")
            archive_size += size
        except RuntimeError as e:
            print(e)
            return

        src_path = os.path.join(
            os.path.dirname(__file__), PlatformType.name(self.platform), "python", "src"
        )
        out_path = os.path.join(os.getcwd(), "build", "intermediate", "app")

        try:
            size = copy_compile(src_path, out_path)
            archive_size += size
        except RuntimeError as e:
            print(e)
            return

        for package in self.site_packages:
            if not os.path.exists(os.path.join(site.getusersitepackages(), package)):
                print(f"Error: Can't find package '{package}'")
                return

            src_path = os.path.join(site.getusersitepackages(), package)
            out_path = os.path.join(
                os.getcwd(), "build", "intermediate", "app", "site-packages"
            )

            try:
                size = copy_compile(src_path, out_path, package)
                archive_size += size
            except RuntimeError as e:
                print(e)
                return

        print(" Copy binaries...")

        src_path = os.path.join(
            os.getcwd(),
            "build",
            "intermediate",
            "deps",
            f"python-{self.py_version}",
            "bin",
            ArchType.name(self.arch),
        )
        out_path = os.path.join(os.getcwd(), "build", "intermediate", "app")

        size = copy_compile(src_path, out_path)
        archive_size += size

        print(" Packing application...")
        if archive_size > 0:
            self.BUILD_VERSION = archive_package(
                os.path.join(os.getcwd(), "build", "intermediate", "app"),
                self.app_version,
                os.path.join(os.getcwd(), "build", "intermediate", "assets", "app.zip"),
            )

    def __create_project__(self, arch: ArchType):
        if self.BUILD_VERSION is None:
            return

        match self.py_version:
            case "3.11.5":
                PYTHON_VERSION = "PYTHON_3_11"
            case _:
                PYTHON_VERSION = "PYTHON_UNKNOWN"

        print(" Generating CMake project...")

        project = CMake(os.path.join(os.getcwd(), "build", "generated"))

        project.set_c_standard(17)
        project.set_cxx_standard(20)

        main_target = project.add_target("main", CMakeTargetType.Executable)
        main_target.add_sources(
            [
                cmake_path("src", "main.cpp"),
                cmake_path("src", "app.cpp"),
                cmake_path("src", "appres.rc"),
            ]
        )
        main_target.add_include_dirs(
            [
                cmake_path("${CMAKE_SOURCE_DIR}", "src"),
                cmake_path("${CMAKE_SOURCE_DIR}", "include"),
                cmake_path(
                    os.getcwd(),
                    "build",
                    "intermediate",
                    "deps",
                    Python(self.platform, self.py_version).path(),
                    "include",
                    "python3.11",
                ),
                cmake_path(
                    os.getcwd(),
                    "build",
                    "intermediate",
                    "deps",
                    LibZip(self.platform).path(),
                    "include",
                ),
                cmake_path(
                    os.getcwd(),
                    "build",
                    "intermediate",
                    "deps",
                    ZLib(self.platform).path(),
                    "include",
                ),
            ]
        )
        main_target.add_link_dirs(
            [
                cmake_path(
                    os.getcwd(),
                    "build",
                    "intermediate",
                    "deps",
                    Python(self.platform, self.py_version).path(),
                    "lib",
                    ArchType.name(arch),
                ),
                cmake_path(
                    os.getcwd(),
                    "build",
                    "intermediate",
                    "deps",
                    LibZip(self.platform).path(),
                    "lib",
                    ArchType.name(arch),
                ),
                cmake_path(
                    os.getcwd(),
                    "build",
                    "intermediate",
                    "deps",
                    ZLib(self.platform).path(),
                    "lib",
                    ArchType.name(arch),
                ),
            ]
        )
        main_target.add_libraries(["python311", "zip", "zlibstatic"])
        main_target.add_precompile_headers([cmake_path("include", "precompiled.h")])
        main_target.add_compile_definitions(
            [f"BUILD_VERSION={self.BUILD_VERSION}", f"{PYTHON_VERSION}"]
        )
        main_target.add_link_options(["/ENTRY:mainCRTStartup"])
        if not self.app_console:
            main_target.add_link_options(["/SUBSYSTEM:WINDOWS"])

        project.generate()

        os.makedirs(
            os.path.join(os.getcwd(), "build", "generated", "resources"), exist_ok=True
        )
        shutil.copytree(
            os.path.join(os.getcwd(), "build", "intermediate", "assets"),
            os.path.join(os.getcwd(), "build", "generated", "resources"),
            dirs_exist_ok=True,
        )
        shutil.copytree(
            os.path.join(
                os.path.join(
                    os.path.dirname(__file__), PlatformType.name(self.platform), "cpp"
                )
            ),
            os.path.join(os.getcwd(), "build", "generated"),
            dirs_exist_ok=True,
        )
