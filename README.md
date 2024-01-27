![splash](https://github.com/a3st/weldbuild/raw/main/splash.png)

## Features

* Popular platforms deployment: Windows, Linux, Android
* Project configuration is simple: One build.py
* Precompiled libraries out of the box: Windows (x64, x86), Linux (x64, x86), Android (armeabi-v7a, arm64-v8a)

## Requirements

1. Android deployment
    * Android SDK
    * Android NDK r26
    * JDK 21
2. Windows deployment
    * Microsoft Visual Studio Build Tools with CMake component
3. Linux deployment
    * CMake

## Example

```python
    from weldbuild import ArchType
    from weldbuild.platforms import WindowsBuild
    
    project = WindowsBuild(
        app_version=(1, 0, 0),
        app_name="Example",
        app_icons={
            "mdpi" : "mdpi.png",
            "hdpi" : "hdpi.png",
            "xhdpi" : "xhdpi.png",
            "xxhdpi" : "xxhdpi.png"
        },
        app_console=True,
        py_version="3.11.5"
    )

    project.configure(ArchType.X64)
    project.build()
```

[Example project](https://github.com/a3st/weldbuild_example_project)

## Roadmap

- Deployments
  - [x] Windows
  - [ ] Linux
  - [ ] Android
- [ ] Custom pre-post build commands

## License

Check LICENSE for additional information.