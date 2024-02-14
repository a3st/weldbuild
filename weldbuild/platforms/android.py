from .. import BuildPlatform, ArchType, PlatformType, Version
from ..utils.gradle import GradleProject
import os

class AndroidBuild(BuildPlatform):
    def __init__(
        self,
        app_version: Version,
        app_package: str,
        app_name: str,
        app_icons: dict,
        py_version: str = "3.11.5"
    ):
        BuildPlatform.__init__(self, PlatformType.Android)
        self.py_version = py_version

        self.app_version = app_version
        self.app_package = app_package
        self.app_name = app_name
        self.app_icons = app_icons

        self.BUILD_VERSION = None


    def configure(self, arch: ArchType):
        BuildPlatform.configure(self, arch)

        self.__unpack_dependicies__()


    def build(self):
        BuildPlatform.build(self)

        
    def __unpack_dependicies__(self):
        pass
    