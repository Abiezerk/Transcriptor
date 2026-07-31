# -*- mode: python ; coding: utf-8 -*-
import os
import whisper

# Ruta real de los assets de Whisper (mel_filters.npz, *.tiktoken).
# Se calcula en tiempo de build en vez de depender de collect_data_files.
WHISPER_ASSETS = os.path.join(os.path.dirname(whisper.__file__), 'assets')
print('>>> Assets de Whisper:', WHISPER_ASSETS, '| existe:', os.path.isdir(WHISPER_ASSETS))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('ffmpeg.exe', '.')],
    datas=[
        ('services', 'services'),
        (WHISPER_ASSETS, os.path.join('whisper', 'assets')),
    ],
    hiddenimports=[
        'whisper',
        'langdetect',
        'numpy',
        'tqdm',
        'tiktoken',
        'tiktoken_ext',
        'tiktoken_ext.openai_public',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Transcriptor de Videos',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TranscriptorDeVideos',
)
