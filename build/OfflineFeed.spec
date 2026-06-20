# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for OfflineFeed (PySide6 + QML).
#
# Build:   pyinstaller build/OfflineFeed.spec
#
# The two things that usually break a PySide6/QML freeze are:
#   1. The qml/ tree (Main.qml, themes/, components/, assets/) not being bundled.
#   2. The Qt5Compat QML plugin (GraphicalEffects — used to recolor SVG icons)
#      being stripped because nothing imports it from Python.
# Both are handled explicitly below.

import os
from PyInstaller.utils.hooks import collect_all, collect_data_files

block_cipher = None

# SPECPATH is defined by PyInstaller and points to the directory containing the spec file (build/)
project_root = os.path.abspath(os.path.join(SPECPATH, '..'))
frontend = os.path.join(project_root, 'frontend')

# --- Bundle the whole QML tree, preserving folder structure ---
qml_datas = []
for root, _dirs, files in os.walk(os.path.join(frontend, 'qml')):
    for f in files:
        abs_path = os.path.join(root, f)
        rel_dir = os.path.relpath(root, frontend)   # e.g. qml/components
        qml_datas.append((abs_path, rel_dir))

# --- Bundle the existing backend assets the UI reads from disk ---
extra_datas = []
backend_viewer = os.path.join(project_root, 'offline_viewer')
if os.path.isdir(backend_viewer):
    for root, _dirs, files in os.walk(backend_viewer):
        for f in files:
            abs_path = os.path.join(root, f)
            rel_dir = os.path.relpath(root, project_root)
            extra_datas.append((abs_path, rel_dir))

# --- Collect PySide6 fully so Qt5Compat / GraphicalEffects ship ---
pyside_datas, pyside_binaries, pyside_hidden = collect_all('PySide6')

hiddenimports = list(pyside_hidden) + [
    'PySide6.QtQml',
    'PySide6.QtQuick',
    'PySide6.QtQuickControls2',
]

a = Analysis(
    [os.path.join(frontend, 'app.py')],
    pathex=[frontend, project_root],
    binaries=pyside_binaries,
    datas=qml_datas + extra_datas + pyside_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OfflineFeed',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                       # GUI app, no console window
    icon=os.path.join(frontend, 'qml', 'assets', 'logo.svg'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OfflineFeed',
)
