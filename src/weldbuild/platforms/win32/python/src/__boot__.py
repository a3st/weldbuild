# Weldbuild boot script for Windows platform

import traceback
import os

try:
    import __app__

except Exception:
    with open(f"crash-info-{os.getpid()}.txt", "w") as f:
        f.write(traceback.format_exc())