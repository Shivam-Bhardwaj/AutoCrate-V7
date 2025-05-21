#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoCrate PyQt Launcher
Version: 0.6.0
This script launches the PyQt6-based AutoCrate application.
"""

import sys
import os
from autocrate_pyqt_gui import main

if __name__ == "__main__":
    # Ensure proper working directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Launch the PyQt application
    sys.exit(main()) 