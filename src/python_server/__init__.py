"""Game server package."""

import os
import sys

# Include internal ``src`` directory in module search path so tests and
# external code can import submodules as ``python_server.<module>``.
_CURRENT_DIR = os.path.dirname(__file__)
_SRC_PATH = os.path.join(_CURRENT_DIR, "src")
if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)
