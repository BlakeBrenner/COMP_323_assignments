# game_config.py — Week 11 Content Pass Demo
# All tunable difficulty values live in this file.
# Change these constants to tune difficulty without editing gameplay code.

# ---------------------------------------------------------------------------
# Window
# ---------------------------------------------------------------------------
WIN_WIDTH = 480
WIN_HEIGHT = 640
FPS = 60

# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------
PLAYER_SPEED = 5
PLAYER_HEALTH = 100
FIRE_COOLDOWN_MS = 250

# ---------------------------------------------------------------------------
# Enemy — base values
# ---------------------------------------------------------------------------
ENEMY_SPEED_MIN = 1.0
ENEMY_SPEED_MAX = 4.0
ENEMY_DAMAGE = 20

# ---------------------------------------------------------------------------
# Spawn rate — progressive difficulty
# ---------------------------------------------------------------------------
SPAWN_DELAY_START_MS = 1200   # initial delay between spawns (ms)
SPAWN_DELAY_MIN_MS = 400      # fastest spawn rate (ms)
SPAWN_RAMP_PER_SEC = 10       # how many ms faster per second of play

# ---------------------------------------------------------------------------
# Enemy scaling
# ---------------------------------------------------------------------------
ENEMY_SPEED_GROWTH = 0.05     # speed bonus per second of play
ENEMY_SPEED_MAX_BONUS = 3.0   # cap on speed bonus

# ---------------------------------------------------------------------------
# Enemy cap
# ---------------------------------------------------------------------------
MAX_ENEMIES = 12              # maximum simultaneous enemies on screen
