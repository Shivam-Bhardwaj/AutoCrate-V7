# AutoCrateWizard.spec
# -*- mode: python ; coding: utf-8 -*-

import os # Keep os for other path operations if needed, but not for SPEC_DIR via __file__
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Exact path to your Streamlit .dist-info folder - This remains an absolute path
streamlit_dist_info_source_path = r'C:\Users\Curio\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\site-packages\streamlit-1.45.0.dist-info'
# The name the folder should have inside the bundle
streamlit_dist_info_bundle_name = 'streamlit-1.45.0.dist-info'


a = Analysis(
    ['run_autocrate_wizard.py'], # Your runner script, located in the project root
    pathex=['.'], # Current directory (project root where .spec and run_autocrate_wizard.py are)
    binaries=[],
    datas=[
        ('wizard_app', 'wizard_app'), # Bundles your 'wizard_app' subfolder.
                                      # This is relative to the .spec file location.
        
        # Explicitly add the .dist-info folder for Streamlit to the bundle's root
        (streamlit_dist_info_source_path, streamlit_dist_info_bundle_name),
        
        *collect_data_files('streamlit', include_py_files=True, subdir='streamlit_data_collected'), 
        *collect_data_files('pandas', include_py_files=True, subdir='pandas'),
        *collect_data_files('plotly', include_py_files=True, subdir='plotly'),
        *collect_data_files('numpy', include_py_files=True, subdir='numpy'),
        *collect_data_files('altair', include_py_files=True, subdir='altair'), 
        *collect_data_files('pyarrow', include_py_files=True, subdir='pyarrow')
    ],
    hiddenimports=[
        'streamlit', 'streamlit.web', 'streamlit.web.server', 'streamlit.web.server.server', 
        'streamlit.web.server.websocket_headers', 'streamlit.web.cli', 'streamlit.runtime', 
        'streamlit.runtime.scriptrunner', 'streamlit.runtime.caching', 'streamlit.logger', 
        'streamlit.caching', 'streamlit.proto.ForwardMsg_pb2', 'streamlit.watcher', 
        'streamlit.watcher.event_based_file_watcher', 'streamlit.watcher.path_watcher',
        'pandas', 'pandas._libs.tslibs.offsets', 
        'numpy', 
        'plotly', 'plotly.graph_objects', 
        'json', 
        'engineio.async_drivers.threading', 
        'babel.numbers', 
        'importlib_metadata', 
        'pkg_resources', 'pkg_resources.py2_warn', 
        'watchdog', 'watchdog.observers', 
        'PIL._imagingtk', 
        'tornado',
        'altair', 'pydeck', 'graphviz', 'pyarrow',                        
        *collect_submodules('streamlit'), 
        *collect_submodules('plotly'),
        *collect_submodules('pandas'),
        *collect_submodules('numpy')
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [], 
    exclude_binaries=True, 
    name='AutoCrateWizard',
    debug=False, 
    bootloader_ignore_signals=False,
    strip=False,
    upx=False, 
    console=True, # KEEP TRUE FOR DEBUGGING
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas, 
    strip=False,
    upx=False, 
    upx_exclude=[],
    name='AutoCrateWizard', 
)
