# Weldbuild boot script for Windows platform

import traceback
import os
import runpy
import sys

try:
    # Find DLL modules, should be always not None
    app_path = next((i for i in sys.path if os.path.basename(i) == ".app"), None)
    os.add_dll_directory(app_path)

    # Run Application
    runpy.run_module('main', run_name='__main__')

except Exception:
    with open(f"crash-info-{os.getpid()}.txt", "w") as f:
        f.write(traceback.format_exc())
