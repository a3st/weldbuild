import os
from . import Package

class App(Package):
    def __init__(self):
        Package.__init__(
            self, 
            os.path.join(os.getcwd(), "build", "intermediate", "app"),
            os.path.join(os.getcwd(), "build", "intermediate", "assets", "app.zip")
        )


class Bootstrap(Package):
    def __init__(self):
        Package.__init__(
            self, 
            os.path.join(os.getcwd(), "build", "intermediate", "bootstrap"),
            os.path.join(os.getcwd(), "build", "intermediate", "assets", "bootstrap.zip")
        )
