#!/usr/bin/env python3
"""Test script to verify fretboardgtr imports work"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from fretboardgtr.fretboard import FretBoard, FretBoardConfig
    from fretboardgtr.notes_creators import ScaleFromName
    print("[SUCCESS] fretboardgtr imports successful!")

    # Test basic functionality
    config = FretBoardConfig()
    fretboard = FretBoard()
    scale = ScaleFromName(root="C", mode="Ionian")
    notes = scale.build()
    print(f"[SUCCESS] Scale creation successful: {notes}")

    print("[SUCCESS] All tests passed!")

except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Runtime error: {e}")
    sys.exit(1)
