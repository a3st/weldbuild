import zipfile
import os

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