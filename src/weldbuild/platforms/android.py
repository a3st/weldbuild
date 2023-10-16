from .. import BuildPlatform, ArchType, PlatformType
from ..utils.gradle import GradleProject
import os

class AndroidBuild(BuildPlatform):
    def __init__(
        self
    ):
        BuildPlatform.__init__(self, PlatformType.Android)


    def configure(self, arch: ArchType):
        BuildPlatform.configure(self, arch)


    def build(self):
        BuildPlatform.build(self)

        


"""
class Android(Platform):
    def __init__(
        self, 
        package_name: str,
        app_name: str,
        arch: ArchType, 
        android_api: int = 28, 
        ndk_version: str = "26.0.10792818",
        sdk_version: int = 34
    ) :
        self.package_name = package_name
        self.app_name = app_name
        self.arch = arch
        self.android_api = android_api
        self.ndk_version = ndk_version
        self.sdk_version = sdk_version

    def configure(self):
        build_path = os.path.join("..", "build", "generated", "android")
        os.makedirs(build_path, exist_ok=True)

        gradle_project = GradleProject(build_path)
        gradle_project.create()
"""
    