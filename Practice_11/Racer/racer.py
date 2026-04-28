import pygame
import random
import sys  # for sys.exit() on quit

# ─────────────────────────────────────────────
#  INITIALISATION
# ─────────────────────────────────────────────
pygame.init()

# ── Window / timing constants ─────────────────
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600
FPS           = 60

# ── Colour palette ────────────────────────────
WHITE   = (255, 255, 255)
BLACK   = (  0,   0,   0)
GRAY    = (100, 100, 100)
DARK    = ( 50,  50,  50)
RED     = (220,  30,  30)
YELLOW  = (255, 215,   0)
GREEN   = ( 30, 200,  30)
BLUE    = ( 30, 100, 220)
ORANGE  = (255, 140,   0)
PURPLE  = (160,  32, 240)
CYAN    = (  0, 220, 220)

# ── Road boundaries (x coordinates) ──────────
ROAD_LEFT  = 60
ROAD_RIGHT = 340

# ─────────────────────────────────────────────
#  COIN TYPES  (Task 1 – weighted coins)
# ─────────────────────────────────────────────
# Each entry: (weight, value, body_colour, outline_colour, label)
# Higher weight = more common; lower weight = rarer.
COIN_TYPES = [
    (60, 1, YELLOW, ORANGE, "$"),           # common bronze – +1
    (25, 3, (192,192,192), (150,150,150), "S"),  # uncommon silver – +3
    (10, 5, YELLOW, (184,134,11), "G"),     # rare gold – +5
    (5, 10, CYAN, (0,180,180), "★"),        # epic gem – +10
]

# Pre-extract weights for random.choices()
_COIN_WEIGHTS = [ct[0] for ct in COIN_TYPES]

# ── Speed-up threshold (Task 2) ───────────────
# Every time the player earns this many coin POINTS, enemies speed up.
SPEED_UP_EVERY = 10

# ── Enemy speed settings ──────────────────────
ENEMY_BASE_SPEED  = 4
ENEMY_SPEED_STEP  = 0.5
ENEMY_SPEED_MAX   = 12

# ── Pygame screen & clock ─────────────────────
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer Game – Extended")
clock  = pygame.time.Clock()

# ── Fonts ─────────────────────────────────────
font_large  = pygame.font.SysFont("Arial", 36, bold=True)
font_medium = pygame.font.SysFont("Arial", 24, bold=True)
font_small  = pygame.font.SysFont("Arial", 18)


# ─────────────────────────────────────────────
#  PLAYER CAR
# ─────────────────────────────────────────────
class PlayerCar:
    """The player-controlled car: moves with arrow keys."""
    
    WIDTH  = 50
    HEIGHT = 80
    SPEED  = 5

    def __init__(self):
        self.x = SCREEN_WIDTH // 2 - self.WIDTH // 2
        self.y = SCREEN_HEIGHT - self.HEIGHT - 20
        self.rect = pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)

    def move(self, keys):
        """Move the car based on arrow keys; stay within road boundaries."""
        if keys[pygame.K_LEFT] and self.rect.left > ROAD_LEFT:
            self.rect.x -= self.SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < ROAD_RIGHT:
            self.rect.x += self.SPEED
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.SPEED
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.SPEED

    def draw(self, surface):
        """Render the player car."""
        pygame.draw.rect(surface, BLUE, self.rect, border_radius=8)
        pygame.draw.rect(surface, (180, 220, 255),
                         (self.rect.x + 8, self.rect.y + 10, 34, 20),
                         border_radius=4)
        pygame.draw.rect(surface, RED,
                         (self.rect.x + 5, self.rect.bottom - 12, 12, 8),
                         border_radius=2)
        pygame.draw.rect(surface, RED,
                         (self.rect.right - 17, self.rect.bottom - 12, 12, 8),
                         border_radius=2)


# ─────────────────────────────────────────────
#  ENEMY CAR
# ─────────────────────────────────────────────
class EnemyCar:
    """An oncoming car that falls from the top."""
    
    WIDTH  = 50
    HEIGHT = 80
    COLORS = [RED, GREEN, ORANGE, PURPLE]

    def __init__(self, speed):
        self.color = random.choice(self.COLORS)
        lane_width = (ROAD_RIGHT - ROAD_LEFT) // 3
        lane = random.randint(0, 2)
        x = ROAD_LEFT + lane * lane_width + (lane_width - self.WIDTH) // 2
        self.rect = pygame.Rect(x, -self.HEIGHT, self.WIDTH, self.HEIGHT)
        self.speed = speed

    def update(self):
        """Move the car downward."""
        self.rect.y += self.speed

    def is_off_screen(self):
        """Return True when car has passed the bottom edge."""
        return self.rect.top > SCREEN_HEIGHT

    def draw(self, surface):
        """Render enemy car."""
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (200, 230, 200),
                         (self.rect.x + 8, self.rect.y + 10, 34, 20),
                         border_radius=4)
        pygame.draw.rect(surface, YELLOW,
                         (self.rect.x + 5, self.rect.bottom - 12, 12, 8),
                         border_radius=2)
        pygame.draw.rect(surface, YELLOW,
                         (self.rect.right - 17, self.rect.bottom - 12, 12, 8),
                         border_radius=2)


# ─────────────────────────────────────────────
#  COIN (Task 1 – weighted types)
# ─────────────────────────────────────────────
class Coin:
    """A collectible coin with weighted value types."""
    
    RADIUS = 12
    SPEED = 4

    def __init__(self, enemies=None):
        """
        Initialize a coin with weighted random type.
        enemies parameter is optional - used to avoid spawning inside cars.
        """
        # Task 1: pick weighted random coin type
        chosen = random.choices(COIN_TYPES, weights=_COIN_WEIGHTS, k=1)[0]
        _, self.value, self.body_color, self.outline_color, self.label = chosen
        
        # Find safe x position (avoid spawning inside enemies)
        margin = self.RADIUS
        if enemies:
            car_rects = [e.rect for e in enemies]
            for _ in range(20):  # Try up to 20 positions
                x = random.randint(ROAD_LEFT + margin, ROAD_RIGHT - margin)
                coin_rect = pygame.Rect(x - margin, -margin * 2, margin * 2, margin * 2)
                if not any(coin_rect.colliderect(r) for r in car_rects):
                    break
            else:  # Fallback if no safe position found
                x = random.randint(ROAD_LEFT + margin, ROAD_RIGHT - margin)
        else:
            x = random.randint(ROAD_LEFT + margin, ROAD_RIGHT - margin)
        
        self.center = [float(x), float(-self.RADIUS)]
        self.rect = pygame.Rect(
            x - self.RADIUS, -self.RADIUS * 2,
            self.RADIUS * 2, self.RADIUS * 2
        )

    def update(self):
        """Move coin downward."""
        self.center[1] += self.SPEED
        self.rect.center = (int(self.center[0]), int(self.center[1]))

    def is_off_screen(self):
        """Return True when coin has passed the bottom edge."""
        return self.center[1] > SCREEN_HEIGHT + self.RADIUS

    def draw(self, surface):
        """Draw the coin with its value label."""
        cx, cy = int(self.center[0]), int(self.center[1])
        
        # Draw coin body and outline
        pygame.draw.circle(surface, self.body_color, (cx, cy), self.RADIUS)
        pygame.draw.circle(surface, self.outline_color, (cx, cy), self.RADIUS, 2)
        
        # Draw coin label
        lbl = font_small.render(self.label, True, self.outline_color)
        surface.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))
        
        # Draw value above coin
        val_lbl = font_small.render(f"+{self.value}", True, self.body_color)
        surface.blit(val_lbl, (cx - val_lbl.get_width() // 2,
                               cy - self.RADIUS - val_lbl.get_height()))


# ─────────────────────────────────────────────
#  ROAD & UI HELPERS
# ─────────────────────────────────────────────
def draw_road(surface, offset):
    """Draw the scrolling road with lane markers."""
    # Green grass verge
    surface.fill((34, 120, 34))
    
    # Grey tarmac
    pygame.draw.rect(surface, GRAY,
                     (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, SCREEN_HEIGHT))
    
    # Road edges
    pygame.draw.rect(surface, WHITE, (ROAD_LEFT, 0, 6, SCREEN_HEIGHT))
    pygame.draw.rect(surface, WHITE, (ROAD_RIGHT - 6, 0, 6, SCREEN_HEIGHT))
    
    # Dashed center lines
    lane_width = (ROAD_RIGHT - ROAD_LEFT) // 3
    for i in range(1, 3):
        lx = ROAD_LEFT + lane_width * i
        for y in range(-80 + offset % 80, SCREEN_HEIGHT, 80):
            pygame.draw.rect(surface, WHITE, (lx - 2, y, 4, 40))


def draw_hud(surface, score, total_coin_value, enemy_speed, coins_into_level):
    """Draw score, coin total, and speed progress bar."""
    # Score (top-left)
    score_lbl = font_medium.render(f"Score: {score}", True, WHITE)
    surface.blit(score_lbl, (8, 8))
    
    # Coin total (top-right) - shows total VALUE, not count
    coin_lbl = font_medium.render(f"Coins: {total_coin_value}", True, YELLOW)
    surface.blit(coin_lbl, (SCREEN_WIDTH - coin_lbl.get_width() - 8, 8))
    
    # Speed progress bar
    bar_x, bar_y, bar_w, bar_h = 8, 38, 130, 10
    pygame.draw.rect(surface, DARK, (bar_x, bar_y, bar_w, bar_h), border_radius=4)
    fill_w = int(bar_w * coins_into_level / SPEED_UP_EVERY)
    if fill_w > 0:
        pygame.draw.rect(surface, ORANGE, (bar_x, bar_y, fill_w, bar_h), border_radius=4)
    pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)
    
    # Speed info
    need = SPEED_UP_EVERY - coins_into_level
    spd_lbl = font_small.render(f"Spd {enemy_speed:.1f}  +spd in {need}pts", True, ORANGE)
    surface.blit(spd_lbl, (bar_x + bar_w + 4, bar_y - 2))


def draw_coin_legend(surface):
    """Show legend of coin values in bottom-right corner."""
    x = SCREEN_WIDTH - 105
    y = SCREEN_HEIGHT - len(COIN_TYPES) * 20 - 10
    for _, value, body, outline, label in COIN_TYPES:
        pygame.draw.circle(surface, body, (x + 8, y + 8), 7)
        pygame.draw.circle(surface, outline, (x + 8, y + 8), 7, 1)
        txt = font_small.render(f"{label} = +{value}", True, WHITE)
        surface.blit(txt, (x + 20, y))
        y += 20


def game_over_screen(score, total_coin_value):
    """Display game over screen with restart option."""
    while True:
        screen.fill(BLACK)
        title = font_large.render("GAME OVER", True, RED)
        s_lbl = font_medium.render(f"Score: {score}", True, WHITE)
        c_lbl = font_medium.render(f"Coins: {total_coin_value}", True, YELLOW)
        r_lbl = font_small.render("Press R — restart   ESC — quit", True, GRAY)
        
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 180))
        screen.blit(s_lbl, (SCREEN_WIDTH // 2 - s_lbl.get_width() // 2, 260))
        screen.blit(c_lbl, (SCREEN_WIDTH // 2 - c_lbl.get_width() // 2, 300))
        screen.blit(r_lbl, (SCREEN_WIDTH // 2 - r_lbl.get_width() // 2, 380))
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()