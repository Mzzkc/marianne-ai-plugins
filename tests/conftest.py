"""Shared test setup for the shipped plugin tree.

Tests import skill scripts in place and run them as subprocesses. Without this,
Python writes ``__pycache__`` into ``marianne/skills/*/scripts/``, and the
release gates that require a cache-free shipped tree fail on every run after
the first.
"""

import os
import sys

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
