from . import Library, PlatformType


class Python(Library):
    def __init__(self, platform: PlatformType, version: str):
        Library.__init__(self, "python", platform, version)


class LibZip(Library):
    def __init__(self, platform: PlatformType):
        Library.__init__(self, "libzip", platform, "1.10.1")


class ZLib(Library):
    def __init__(self, platform: PlatformType):
        Library.__init__(self, "zlib", platform, "1.3")
