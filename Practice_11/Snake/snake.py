import pygame
import random
import sys

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
CELL    = 20
COLS    = 25
ROWS    = 25
PANEL_H = 50          # top HUD height
BAR_H   = 8           # timer-slider bar height (drawn below each food cell)
BAR_PAD = 2           # gap between cell bottom and slider bar
BOTTOM  = 12          # extra space at the bottom so bars are not clipped

WIDTH   = COLS * CELL
HEIGHT  = ROWS * CELL + PANEL_H + BOTTOM

BASE_FPS      = 60
BASE_MOVE     = 8     # frames between snake steps
FOOD_PER_LEVEL = 4    # food eaten to reach next level
FOOD_LIFETIME  = 6.0  # seconds before a food piece disappears

# ─────────────────────────────────────────────
#  COLOURS
# ─────────────────────────────────────────────
BG_COLOR      = ( 15,  15,  15)
GRID_COLOR    = ( 30,  30,  30)
SNAKE_HEAD    = ( 50, 220,  50)
SNAKE_BODY    = ( 30, 160,  30)
SNAKE_OUTLINE = ( 10,  90,  10)
WALL_COLOR    = ( 80,  80,  80)
TEXT_COLOR    = (255, 255, 255)
GOLD          = (255, 215,   0)
RED           = (220,  30,  30)
BLUE          = (100, 200, 255)

# ─────────────────────────────────────────────
#  FOOD TYPES  — (weight, points, colour, shine, label)
# ─────────────────────────────────────────────
FOOD_TYPES = [
    (60,  1, (220,  50,  50), (255, 120, 120), "normal"),  # red   — most common
    (25,  3, ( 50, 200, 255), (150, 230, 255), "bonus"),   # blue
    (10,  5, (255, 200,   0), (255, 240, 120), "rare"),    # gold
    ( 5, 10, (200,  50, 220), (230, 130, 255), "epic"),    # purple — rarest
]
_WEIGHTS = [ft[0] for ft in FOOD_TYPES]

# ─────────────────────────────────────────────
#  PYGAME SETUP  (imported by main.py)
# ─────────────────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock  = pygame.time.Clock()

font_large  = pygame.font.SysFont("Consolas", 40, bold=True)
font_medium = pygame.font.SysFont("Consolas", 24, bold=True)
font_small  = pygame.font.SysFont("Consolas", 16)


# ─────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────
def cell_to_px(col, row):
    """Grid cell → top-left pixel, offset by top panel."""
    return col * CELL, row * CELL + PANEL_H


# ─────────────────────────────────────────────
#  SNAKE
# ─────────────────────────────────────────────
class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        cx, cy         = COLS // 2, ROWS // 2
        self.body      = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.next_dir  = (1, 0)
        self.grew      = False

    def set_direction(self, dx, dy):
        # Ignore direction if it would reverse the snake
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.next_dir = (dx, dy)

    def step(self):
        """Move one cell. Returns False on wall/self collision."""
        self.direction = self.next_dir
        hx, hy = self.body[0]
        new_head = (hx + self.direction[0], hy + self.direction[1])

        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            return False
        if new_head in self.body:
            return False

        self.body.insert(0, new_head)
        if self.grew:
            self.grew = False   # keep tail this turn
        else:
            self.body.pop()
        return True

    def grow(self):
        self.grew = True

    def draw(self, surface):
        for i, (col, row) in enumerate(self.body):
            px, py = cell_to_px(col, row)
            color  = SNAKE_HEAD if i == 0 else SNAKE_BODY
            pygame.draw.rect(surface, color,
                             (px+1, py+1, CELL-2, CELL-2), border_radius=4)
            pygame.draw.rect(surface, SNAKE_OUTLINE,
                             (px+1, py+1, CELL-2, CELL-2), 1, border_radius=4)
            if i == 0:
                self._draw_eyes(surface, px, py)

    def _draw_eyes(self, surface, px, py):
        dx, dy = self.direction
        offsets = {
            ( 1, 0): [(12, 5),  (12, 13)],
            (-1, 0): [(5,  5),  (5,  13)],
            (0, -1): [(5,  5),  (13,  5)],
            (0,  1): [(5, 13),  (13, 13)],
        }
        for ex, ey in offsets.get((dx, dy), [(5, 5), (13, 5)]):
            pygame.draw.circle(surface, TEXT_COLOR, (px+ex, py+ey), 3)
            pygame.draw.circle(surface, BG_COLOR,   (px+ex, py+ey), 1)


# ─────────────────────────────────────────────
#  FOOD
# ─────────────────────────────────────────────
class Food:
    """
    One food piece. Has:
    - weighted random type (different points per type)
    - 6-second lifetime shown as a shrinking slider bar below the cell
    """

    def __init__(self):
        self.pos      = (0, 0)
        self.points   = 1
        self.color    = (220, 50, 50)
        self.shine    = (255, 120, 120)
        self._elapsed = 0.0   # ms elapsed since spawn

    def respawn(self, snake_body):
        """Pick a free cell and a random weighted food type. Reset timer."""
        free = [
            (c, r)
            for c in range(COLS)
            for r in range(ROWS)
            if (c, r) not in snake_body
        ]
        if not free:
            return

        self.pos = random.choice(free)

        # Weighted random: higher weight = more likely
        chosen = random.choices(FOOD_TYPES, weights=_WEIGHTS, k=1)[0]
        _, self.points, self.color, self.shine, _ = chosen

        self._elapsed = 0.0   # restart timer

    def update(self, dt_ms):
        """
        Add dt_ms to elapsed time.
        Returns True when 6 seconds have passed → food should be removed.
        """
        self._elapsed += dt_ms
        return self._elapsed >= FOOD_LIFETIME * 1000

    def time_frac(self):
        """How much time is LEFT: 1.0 = just spawned, 0.0 = expired."""
        return max(0.0, 1.0 - self._elapsed / (FOOD_LIFETIME * 1000))

    def draw(self, surface):
        col, row = self.pos
        px, py   = cell_to_px(col, row)
        cx, cy   = px + CELL // 2, py + CELL // 2
        r        = CELL // 2 - 2

        # Food circle
        pygame.draw.circle(surface, self.color, (cx, cy), r)
        pygame.draw.circle(surface, self.shine, (cx-3, cy-3), 4)

        # Point label on the food (+1 / +3 / +5 / +10)
        lbl = font_small.render(f"+{self.points}", True, TEXT_COLOR)
        surface.blit(lbl, (cx - lbl.get_width()//2, cy - lbl.get_height()//2))

        # ── Timer slider bar below the cell ──────────────────────
        frac = self.time_frac()

        # Colour: green → yellow → red
        if frac > 0.5:
            bar_col = ( 50, 210,  50)   # green
        elif frac > 0.25:
            bar_col = (255, 200,   0)   # yellow
        else:
            bar_col = (210,  40,  40)   # red

        bar_x = px
        bar_y = py + CELL + BAR_PAD
        bar_w = CELL

        # Dark background track (full width)
        pygame.draw.rect(surface, (40, 40, 40),
                         (bar_x, bar_y, bar_w, BAR_H), border_radius=3)
        # Coloured fill (shrinks right as time runs out)
        fill = max(1, int(bar_w * frac))
        pygame.draw.rect(surface, bar_col,
                         (bar_x, bar_y, fill, BAR_H), border_radius=3)


# ─────────────────────────────────────────────
#  DRAWING HELPERS
# ─────────────────────────────────────────────
def draw_field(surface):
    """Dark background + grid lines + border wall."""
    pygame.draw.rect(surface, BG_COLOR, (0, PANEL_H, WIDTH, HEIGHT - PANEL_H))
    for col in range(COLS):
        for row in range(ROWS):
            px, py = cell_to_px(col, row)
            pygame.draw.rect(surface, GRID_COLOR, (px, py, CELL, CELL), 1)
    # Border around only the grid area, not the slider zone
    pygame.draw.rect(surface, WALL_COLOR,
                     (0, PANEL_H, WIDTH, ROWS * CELL), 3)


def draw_hud(surface, score, level):
    """Top panel: score, level, and food-type legend."""
    pygame.draw.rect(surface, (20, 20, 40), (0, 0, WIDTH, PANEL_H))
    pygame.draw.line(surface, WALL_COLOR, (0, PANEL_H), (WIDTH, PANEL_H), 2)

    score_lbl = font_medium.render(f"Score: {score}", True, GOLD)
    level_lbl = font_medium.render(f"Level: {level}", True, BLUE)
    surface.blit(score_lbl, (10, PANEL_H//2 - score_lbl.get_height()//2))
    surface.blit(level_lbl, (WIDTH - level_lbl.get_width() - 10,
                              PANEL_H//2 - level_lbl.get_height()//2))

    # Small food-type colour guide in the centre of the HUD
    lx = WIDTH//2 - 85
    for _, pts, col, _, _ in FOOD_TYPES:
        pygame.draw.circle(surface, col, (lx + 6, PANEL_H//2), 6)
        t = font_small.render(f"+{pts}", True, col)
        surface.blit(t, (lx + 16, PANEL_H//2 - t.get_height()//2))
        lx += 46


def end_screen(score, level):
    """Game-over overlay. R = restart, ESC = quit. Returns True to restart."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    lines = [
        (font_large,  "GAME OVER",              RED),
        (font_medium, f"Score: {score}",        GOLD),
        (font_medium, f"Level: {level}",        BLUE),
        (font_small,  "R — restart  ESC — quit",TEXT_COLOR),
    ]
    total_h = sum(f.get_height() + 10 for f, _, _ in lines)
    y = HEIGHT // 2 - total_h // 2
    for fnt, text, color in lines:
        lbl = fnt.render(text, True, color)
        screen.blit(lbl, (WIDTH//2 - lbl.get_width()//2, y))
        y += lbl.get_height() + 10

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:      return True
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
        clock.tick(30)
