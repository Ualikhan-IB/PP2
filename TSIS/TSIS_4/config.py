# config.py
import pygame

# Screen dimensions
CELL = 20
COLS = 30
ROWS = 25
PANEL_H = 60
BAR_H = 8
BAR_PAD = 2
BOTTOM = 12

WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + PANEL_H + BOTTOM

# Game settings
BASE_FPS = 60
BASE_MOVE = 8
FOOD_PER_LEVEL = 4
FOOD_LIFETIME = 6000  # milliseconds
POWERUP_DURATION = 5000
POWERUP_LIFETIME = 8000
OBSTACLES_FROM_LEVEL = 3

# Colors
BG_COLOR = (15, 15, 15)
GRID_COLOR = (30, 30, 30)
SNAKE_HEAD = (50, 220, 50)
SNAKE_BODY = (30, 160, 30)
SNAKE_OUTLINE = (10, 90, 10)
WALL_COLOR = (80, 80, 80)
TEXT_COLOR = (255, 255, 255)
GOLD = (255, 215, 0)
BLUE = (100, 200, 255)
RED = (220, 30, 30)
DARK_RED = (139, 0, 0)
PURPLE = (200, 50, 220)
ORANGE = (255, 165, 0)

# Food types (weight, points, color, shine)
FOOD_TYPES = [
    (60, 1, (220, 50, 50), (255, 120, 120), "normal"),
    (25, 3, (50, 200, 255), (150, 230, 255), "bonus"),
    (10, 5, (255, 200, 0), (255, 240, 120), "rare"),
    (5, 10, (200, 50, 220), (230, 130, 255), "epic"),
]

# Power-up types
POWERUP_TYPES = [
    ("speed_boost", (100, 255, 100), "⚡"),
    ("slow_motion", (100, 100, 255), "🐢"),
    ("shield", (255, 200, 0), "🛡"),
]

# Database config - CHANGE THIS TO YOUR PASSWORD
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'snake_game',
    'user': 'postgres',
    'password': 'Ualikhan_PP2'  }