import os
from io import StringIO
from .. import BuildPlatform, ArchType, PlatformType, compile_sources, copy_binaries
from ..deps import Python, LibZip, ZLib
from ..packages import App, Bootstrap
from ..utils.png2ico import ICOParser

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
        print(" Checking missing dependicies...")
        Python(self.platform, self.py_version).unpack()
        LibZip(self.platform).unpack()
        ZLib(self.platform).unpack()


    def __package__(self):
        print(" Cooking python scripts...")

        app_size = 0
        bootstrap_size = 0
        
        src_path = os.path.join(os.getcwd(), "src")
        out_path = os.path.join(os.getcwd(), "build", "intermediate", "app")
        cache_path = os.path.join(out_path, ".sources")
        
        out_cache = StringIO()
        if os.path.exists(cache_path):
            result = compile_sources(src_path, out_path, cache_path, out_cache)
        else:
            result = compile_sources(src_path, out_path, None, out_cache)

        if result is not None:
            with open(cache_path, "wt") as fp:
                fp.write(out_cache.getvalue())
            app_size += result
        else:
            print(" Cooking python scripts ended with error")
            return

        src_path = os.path.join(os.path.dirname(__file__), PlatformType.name(self.platform))
        out_path = os.path.join(os.getcwd(), "build", "intermediate", "bootstrap")
        cache_path = os.path.join(out_path, ".sources")

        out_cache = StringIO()
        if os.path.exists(cache_path):
            result = compile_sources(src_path, out_path, cache_path, out_cache)
        else:
            result = compile_sources(src_path, out_path, None, out_cache)

        if result is not None:
            with open(cache_path, "wt") as fp:
                fp.write(out_cache.getvalue())
            bootstrap_size += result
        else:
            print(" Cooking python scripts ended with error")
            return
        
        print(" Copy binaries...")
        
        src_path = os.path.join(os.getcwd(), "lib", ArchType.name(self.arch))
        out_path = os.path.join(os.getcwd(), "build", "intermediate", "app")
        cache_path = os.path.join(out_path, ".binaries")

        out_cache = StringIO()
        if os.path.exists(cache_path):
            result = copy_binaries(src_path, out_path, cache_path, out_cache)
        else:
            result = copy_binaries(src_path, out_path, None, out_cache)

        if result > 0:
            with open(cache_path, "wt") as fp:
                fp.write(out_cache.getvalue())
            app_size += result

        src_path = os.path.join(os.getcwd(), "build", "intermediate", "deps", f"python-{self.py_version}", "bin", ArchType.name(self.arch))
        out_path = os.path.join(os.getcwd(), "build", "intermediate", "bootstrap")
        cache_path = os.path.join(out_path, ".binaries")

        out_cache = StringIO()
        if os.path.exists(cache_path):
            result = copy_binaries(src_path, out_path, cache_path, out_cache)
        else:
            result = copy_binaries(src_path, out_path, None, out_cache)

        if result > 0:
            with open(cache_path, "wt") as fp:
                fp.write(out_cache.getvalue())
            bootstrap_size += result

        print(" Packing archives...")
        if app_size > 0:
            App().package()
        if bootstrap_size > 0:
            Bootstrap().package()
