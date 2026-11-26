#!/usr/bin/env python3
"""Entrypoint for the news-image entry: draw the front page.

Run from anywhere: `python3 main.py` regenerates entry.png in this
directory by executing render.py (PIL only, no photos)."""
import os
import subprocess
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    return subprocess.call(
        [sys.executable, os.path.join(here, "render.py")], cwd=here
    )


if __name__ == "__main__":
    raise SystemExit(main())
