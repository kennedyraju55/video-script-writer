"""Shared fixtures for Video Script Writer tests."""

import sys
import os

# Ensure src/ and project root are importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
