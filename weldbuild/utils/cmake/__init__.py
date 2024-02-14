import os

def cmake_path(path: str, *paths: str) -> str:
    return os.path.join(path, *paths).replace('\\', '/')


class CMakeTargetType:
    Executable = 0
    Library = 1


class CMakeTarget:
    def __init__(self, name: str, type: CMakeTargetType):
        self.name = name

        self.type = type
        self.is_shared = False

        self.sources = []
        self.precompile_headers = []
        self.libraries = []

        self.include_dirs = []
        self.link_dirs = []

        self.compile_definitions = []
        self.link_options = []
    

    def add_sources(self, sources: list[str]):
        self.sources.extend(sources)

    
    def set_as_shared(self):
        self.is_shared = True


    def add_include_dirs(self, dirs: list[str]):
        self.include_dirs.extend(dirs)

    
    def add_link_dirs(self, dirs: list[str]):
        self.link_dirs.extend(dirs)


    def add_libraries(self, libraries: list[str]):
        self.libraries.extend(libraries)


    def add_precompile_headers(self, headers: list[str]):
        self.precompile_headers.extend(headers)

    
    def add_compile_definitions(self, definitions: list[str]):
        self.compile_definitions.extend(definitions)

    
    def add_link_options(self, options: list[str]):
        self.link_options.extend(options)


class CMake:
    def __init__(self, out_path: str):
        self.out_path = out_path
        self.targets = []
        self.cxx_standard = 11
        self.c_standard = 11

    
    def set_cxx_standard(self, value: int):
        self.cxx_standard = value
    

    def set_c_standard(self, value: int):
        self.c_standard = value
    

    def add_target(self, name: str, type: CMakeTargetType) -> CMakeTarget:
        self.targets.append(CMakeTarget(name, type))
        return self.targets[-1]

    
    def generate(self):
        os.makedirs(self.out_path, exist_ok=True)

        with open(os.path.join(self.out_path, "CMakeLists.txt"), "wt") as fp:
            fp.write("cmake_minimum_required(VERSION 3.25.3)\n\n")
            fp.write(f"set(CMAKE_C_STANDARD {self.c_standard})\n")
            fp.write(f"set(CMAKE_CXX_STANDARD {self.cxx_standard})\n\n")

            for target in self.targets:
                value = " ".join(target.sources)
                if target.type is CMakeTargetType.Executable:
                    fp.write(f"add_executable({target.name} {value})\n")
                elif target.type is CMakeTargetType.Library:
                    if target.is_shared:
                        lib_type = "SHARED"
                    else:
                        lib_type = "STATIC"
                    fp.write(f"add_library({target.name} {lib_type} {value})\n")
                
                if len(target.include_dirs) != 0:
                    value = " ".join(target.include_dirs)
                    fp.write(f"target_include_directories({target.name} PRIVATE {value})\n")

                if len(target.link_dirs) != 0:
                    value = " ".join(target.link_dirs)
                    fp.write(f"target_link_directories({target.name} PRIVATE {value})\n")

                if len(target.libraries) != 0:
                    value = " ".join(target.libraries)
                    fp.write(f"target_link_libraries({target.name} {value})\n")

                if len(target.precompile_headers) != 0:
                    value = " ".join(target.precompile_headers)
                    fp.write(f"target_precompile_headers({target.name} PRIVATE {value})\n")

                if len(target.compile_definitions) != 0:
                    value = " ".join(target.compile_definitions)
                    fp.write(f"target_compile_definitions({target.name} PRIVATE {value})\n")

                if len(target.link_options) != 0:
                    value = " ".join(target.link_options)
                    fp.write(f"target_link_options({target.name} PRIVATE {value})\n")
            


