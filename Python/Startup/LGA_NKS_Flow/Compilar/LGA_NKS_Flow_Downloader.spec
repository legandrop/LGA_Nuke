# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['LGA_NKS_Flow_Downloader.py'],
    pathex=[],
    binaries=[],
    datas=[('Data/no_icon.ico', 'Data'), ('Data/LGA.ico', 'Data'), ('Data/settings_off.png', 'Data'), ('Data/settings_on.png', 'Data'), ('Data/CTkScrollableDropdown/ctk_scrollable_dropdown.py', 'Data/CTkScrollableDropdown'), ('Data/LGA_NKS_Flow_Downloader_CCTK_Theme.json', 'Data')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='LGA_NKS_Flow_Downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Data\\LGA.ico'],
)
