#!/usr/bin/env python3
"""Local preview helper: render the front page to entry.png next to this file.

Not used by the grader (main.py is the entrypoint); handy for checking the
image by eye before a submission.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import build


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "entry.png")
    build().save(path, "PNG")
    print("wrote", path)


if __name__ == "__main__":
    main()
