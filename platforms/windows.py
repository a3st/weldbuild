import os
from .. import BuildPlatform, ArchType, PlatformType
from ..deps import Python, LibZip, ZLib
from ..utils.png2ico import ICOParser 
from ..packages import AppPackage, BootstrapPackage


class WindowsBuild(BuildPlatform):
    def __init__(
        self,
        app_name: str,
        app_icons: dict,
        py_version: str = "3.11.5"
    ):
        BuildPlatform.__init__(self, PlatformType.Windows)
        self.py_version = py_version

        self.app_name = app_name
        self.app_icons = app_icons


    def configure(self, arch: ArchType):
        BuildPlatform.configure(self, arch)

        self.__unpack_dependicies__()
        self.__make_icon__()
        self.__package__()


    def build(self):
        BuildPlatform.build(self)


    def __make_icon__(self):
        os.makedirs(os.path.join(os.getcwd(), "build", "intermediate", "assets"), exist_ok=True)
        ICOParser(self.app_icons.values()).save_to_file(os.path.join(os.getcwd(), "build", "intermediate", "assets", "app.ico"))


    def __unpack_dependicies__(self):
        print(f" Checking missing dependicies...")
        Python(self.platform, self.py_version).unpack()
        LibZip(self.platform).unpack()
        ZLib(self.platform).unpack()


    def __package__(self):
        print(f" Cooking python scripts...")
        AppPackage(self.arch).package()
        BootstrapPackage(self.platform, self.arch, self.py_version).package()
