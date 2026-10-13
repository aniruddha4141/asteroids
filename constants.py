SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
PLAYER_RADIUS = 20
LINE_WIDTH = 2
PLAYER_TURN_SPEED = 300
PLAYER_SPEED = 200
ASTEROID_MIN_RADIUS = 20
ASTEROID_KINDS = 3
ASTEROID_SPAWN_RATE_SECONDS = 0.8
ASTEROID_MAX_RADIUS = ASTEROID_MIN_RADIUS * ASTEROID_KINDS
SHOT_RADIUS = 5
PLAYER_SHOOT_SPEED = 500
PLAYER_SHOOT_COOLDOWN_SECONDS = 0.3

# Colors
COLOR_BG = (10, 12, 22)
COLOR_WHITE = (245, 245, 255)
COLOR_CYAN = (0, 245, 255)
COLOR_PINK = (255, 50, 130)
COLOR_ORANGE = (255, 140, 25)
COLOR_GREEN = (60, 255, 120)
COLOR_YELLOW = (255, 230, 40)
COLOR_PURPLE = (190, 80, 255)
COLOR_RED = (255, 60, 60)
COLOR_GRAY = (130, 135, 150)
COLOR_PANEL = (20, 24, 42, 220)
COLOR_PANEL_BORDER = (0, 200, 255)

# Game Rules
PLAYER_MAX_LIVES = 3
PLAYER_INVULNERABLE_TIME = 2.5
POWERUP_RADIUS = 16
POWERUP_DURATION = 8.5
POWERUP_DROP_CHANCE = 0.35

# Difficulty Levels
DIFF_EASY = "EASY"
DIFF_NORMAL = "NORMAL"
DIFF_HARD = "HARD"
DIFF_EXTREME = "EXTREME"

DIFFICULTIES = {
    DIFF_EASY: {
        "name": "EASY",
        "spawn_rate": 1.25,
        "speed_mult": 0.75,
        "lives": 5,
        "drop_chance": 0.50,
        "score_mult": 1.0,
        "color": COLOR_GREEN,
        "desc": "Calm asteroid field, 5 lives, and generous power-up drop rates.",
    },
    DIFF_NORMAL: {
        "name": "NORMAL",
        "spawn_rate": 0.80,
        "speed_mult": 1.00,
        "lives": 3,
        "drop_chance": 0.35,
        "score_mult": 1.25,
        "color": COLOR_CYAN,
        "desc": "The balanced classic arcade challenge with 3 lives.",
    },
    DIFF_HARD: {
        "name": "HARD",
        "spawn_rate": 0.52,
        "speed_mult": 1.35,
        "lives": 2,
        "drop_chance": 0.22,
        "score_mult": 1.75,
        "color": COLOR_ORANGE,
        "desc": "High velocity meteors, swarming waves, and only 2 lives.",
    },
    DIFF_EXTREME: {
        "name": "EXTREME",
        "spawn_rate": 0.32,
        "speed_mult": 1.75,
        "lives": 1,
        "drop_chance": 0.12,
        "score_mult": 2.50,
        "color": COLOR_RED,
        "desc": "Hyper-speed death field, 1 LIFE ONLY, massive score multiplier!",
    },
}

# Game States
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"
STATE_OPTIONS = "options"
STATE_HANGAR = "hangar"
