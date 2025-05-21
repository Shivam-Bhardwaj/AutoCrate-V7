# AutoCratePyQt.spec (Single-File Executable, No Console)
# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# This .spec file should be in your project root (e.g., AutoCrate-V7).
# pathex will ensure PyInstaller looks for your main script in this root.

a = Analysis(
    ['autocrate_pyqt_gui.py'], # Your main PyQt application script
    pathex=['.'],              # Current directory (project root)
    binaries=[],               # PyInstaller usually finds PyQt binaries. Add specific DLLs if needed.
    datas=[
        # Bundle the entire 'wizard_app' folder.
        # This path is relative to the location of this .spec file.
        ('wizard_app', 'wizard_app') 
    ],
    hiddenimports=[
        'PyQt6', 
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip', # Often needed for PyQt
        'json',
        'datetime',
        'logging',
        'math',
        'os',
        'sys',
        # Add other direct or indirect imports from your wizard_app modules if they cause issues.
        # For example, if your logic used pandas:
        # 'pandas', 
        # 'numpy', 
        # And then you might need to add pandas data files to 'datas' as well:
        # *collect_data_files('pandas', subdir='pandas', include_py_files=True),
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0, # Set to 0 for easier debugging initially
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries, # Include binaries in the EXE for one-file
    a.zipfiles, # Include zipfiles (usually from PYZ)
    a.datas,    # Include datas in the EXE for one-file
    [],         # Runtime hooks list
    name='AutoCratePyQtGUI', # Name of your executable
    debug=False, 
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,   # Compresses the executable; set to False if it causes issues or for faster builds
    console=False, # IMPORTANT: Set to False to hide the console window for release
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # windowed=True, # Alternative to console=False for explicitly windowed app
    # icon='your_icon.ico' # Optional: You can add an icon for your app
)

# For a one-file build, the COLLECT section is NOT used as everything is in the EXE.
