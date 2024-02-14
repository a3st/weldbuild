import os

class GradleProject:
    def __init__(self, dest_dir: str):
        self.dest_dir = dest_dir

    
    def create(self):
        self.__generate_settings__()
        self.__generate_build__()

    
    def __generate_build__(self):
        with open(os.path.join(self.dest_dir, "build.gradle"), "w") as f:
            f.write(f"""
plugins {{
    id 'com.android.application' version '8.1.1'
}}
                    
android {{
    compileSdk {34}
    ndkVersion '{'26.0.10792818'}'

    defaultConfig {{
        applicationId '{'com.application.name'}'
        minSdkVersion {28}
        targetSdkVersion {34}

        externalNativeBuild {{
            cmake {{
                arguments '-DANDROID_STL=c++_static'
            }}
        }}
    }}
    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android.txt'),
                    'proguard-rules.pro'
            ndk {{
                abiFilters "arm64-v8a"
            }}
        }}
        debug {{
            ndk {{
                abiFilters "arm64-v8a"
            }}
        }}
    }}
    externalNativeBuild {{
        cmake {{
            path 'src/main/cpp/CMakeLists.txt'
        }}
    }}
    namespace '{'com.application.name'}'
}}

dependencies {{
    implementation fileTree(dir: 'libs', include: ['*.jar'])
}}
            """)

    
    def __generate_settings__(self):
        with open(os.path.join(self.dest_dir, "settings.gradle"), "w") as f:
            f.write("""
pluginManagement {
    repositories {
        gradlePluginPortal()
        google()
        mavenCentral()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
            """)
        