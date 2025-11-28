# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('slowplay/resources/*', 'slowplay/resources')]
datas += [(".venv/lib/python3.12/site-packages/tkinterdnd2/tkdnd/linux-x64/*", "tkinterdnd2/tkdnd/linux-x64")]
binaries = []
hiddenimports = ['PIL._tkinter_finder']
tmp_ret = collect_all('tkinterdnd2')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

gst_include_plugins = [
    # gstreamer
    "coreelements",
    # gstreamer-plugins-base
    "alsa",  # Linux audio output
    "jack",
    "oss",
    "oss4",
    "audioconvert",
    "audiomixer",
    "audiorate",
    "audioresample",
    "ogg",
    "playback",
    "rawparse",
    "typefindfunctions",
    "volume",
    "vorbis",
    "wavenc",
    # gstreamer-plugins-good
    "apedemux",
    "audioparsers",
    "auparse",
    "autodetect",
    "directsound", # Windows audio output
    "flac",
    "id3demux",
    "isomp4",
    "libav",
    "lame",
    "apetag",
    "mpg123",
    "osxaudio",  # macOS audio output
    "pulseaudio",  # Linux audio output
    "replaygain",
    "speex",
    "taglib",
    "twolame",
    "wavparse",
    # gstreamer-plugins-bad
    "wasapi",  # Windows audio output
    "soundtouch",  # soundtouch plugins
]

a = Analysis(
    ['sp-launch.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['.'],
    hooksconfig={
        "gstreamer": {
            "include_plugins": gst_include_plugins,
        },
    },
    runtime_hooks=[],
    excludes=['PyQt5'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='slowplay',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    upx=True,
        upx_exclude=[],
        name='slowplay',
)
