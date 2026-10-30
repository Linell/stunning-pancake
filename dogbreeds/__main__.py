import os
import sys

from .cli import main

try:
    code = main()
    sys.stdout.flush()
except BrokenPipeError:
    # e.g. `python -m dogbreeds | head`: exit quietly, as other Unix tools do.
    os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    code = 1
sys.exit(code)
