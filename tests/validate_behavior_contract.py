#!/usr/bin/env python3
"""Backward-compatible command. Runs utility tests, NOT independent LLM evals."""
import sys
import unittest
from pathlib import Path
sys.dont_write_bytecode = True
root = Path(__file__).resolve().parent
suite = unittest.defaultTestLoader.discover(str(root), pattern="test_workspace.py")
result = unittest.TextTestRunner(verbosity=2).run(suite)
print("PROGRAM_TESTS_ONLY: no independent AI behavior or product advantage measured")
sys.exit(0 if result.wasSuccessful() else 1)
