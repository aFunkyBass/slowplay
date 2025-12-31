# Definitions

APP_TITLE = "SlowPlay"
APP_NAME = "slowplay"
APP_DESCRIPTION = "SlowPlay is a simple audio player with speed/pitch \
change capabilities, based on GStreamer."

APP_VERSION = "0.3.0b"

APP_URL = "https://github.com/aFunkyBass/slowplay"

INITIAL_GEOMETRY = "800x350"

THEME_NAME = "clam"         # tkInter Theme
LBL_FONT_SIZE = 14          # Label standard size

DEFAULT_SPEED = 100         # Default speed (percent)
MIN_SPEED_PERCENT = 50      # Minimum speed (percent)
MAX_SPEED_PERCENT = 150     # Maximum speed (percent)
STEPS_SPEED = 5             # Speed incr/decr steps (percent)

DEFAULT_SEMITONES = 0       # Default semitone transpose (0 = no transpose)
MIN_PITCH_SEMITONES = -12   # Maximum semitones transpose down
MAX_PITCH_SEMITONES = 12    # Maximum semitones transpose up
STEPS_SEMITONES = 1         # Transpose incr/decr steps (semitones)

DEFAULT_CENTS = 0           # Default detune in cents (0 = no detune)
MIN_PITCH_CENTS = -50       # Maximum detune down (cents)
MAX_PITCH_CENTS = 50        # Maximum detune up (cents)

DEFAULT_VOLUME = 100
MIN_VOLUME = 0
MAX_VOLUME = 100

STEPS_SEC_MOVE_1 = 5        # Seconds to move using the num keypad +/- min
STEPS_SEC_MOVE_2 = 10       # Seconds to move using the num keypad +/- med
STEPS_SEC_MOVE_3 = 15       # Seconds to move using the num keypad +/- max

# Song position update interval in milliseconds
UPDATE_INTERVAL = 20

# Status bar message disappear time
STATUS_BAR_TIMEOUT = 3000

# Allowed audio files extensions (open)
OPEN_EXTENSIONS_FILTER = (
    'mp3',
    'wav',
    'flac',
    'aif',
    'ogg',
    'aac',
    'alac',
    'wma',
    'm4a'
)

# Allowed audio files extensions (save)
SAVE_EXTENSIONS_FILTER = (
    'mp3',
    'wav',
)

# Default save file extension
SAVE_DEFAULT_EXTENSION = "mp3"

# YouTube constants
YTDLP_CMD = "yt-dlp"                   # Command to execute for video managing
YT_AUDIO_FORMAT_EXTENSION = "mp3"      # default audio extraction format 
YT_THUMB_FORMAT_EXTENSION = "png"      # default thumbnail extraction format