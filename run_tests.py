#!/usr/bin/env python3
"""Simple test runner for ISA regex tests."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    try:
        import pytest
        sys.exit(pytest.main([
            "tests/test_constants.py", 
            "-v",
            "--tb=short"
        ]))
    except ImportError:
        print("pytest not installed. Install with: pip install pytest")
        sys.exit(1)
