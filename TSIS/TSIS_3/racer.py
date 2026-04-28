"""
Racer Game Core - All game mechanics
Fixed: Player movement, event handling, all features
"""

import pygame
import random
import math

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
ROAD_LEFT = 60
ROAD_RIGHT = 340
LANE_COUNT = 3
LANE_WIDTH = (ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK = (50, 50, 50)
RED = (220, 30, 30)
YELLOW = (255, 215, 0)
GREEN = (30, 200, 30)
BLUE = (30, 100, 220)
ORANGE = (255, 140, 0)
PURPLE = (160, 32, 240)
CYAN = (0, 220, 220)
BROWN = (139, 69, 19)
DARK_RED = (139, 0, 0)

# Coin types
COIN_TYPES = [
    (60, 1, YELLOW, ORANGE, "$"),
    (25, 3, (192, 192, 192), (150, 150, 150), "S"),
    (10, 5, YELLOW, (184, 134, 11), "G"),
    (5, 10, CYAN, (0, 180, 180), "★"),
]
_COIN_WEIGHTS = [ct[0] for ct in COIN_TYPES]

# Power-ups
POWERUP_NITRO = "nitro"
POWERUP_SHIELD = "shield"
POWERUP_REPAIR = "repair"

POWERUP_TYPES = [
    (POWERUP_NITRO, YELLOW, "N", "Nitro Boost!", 300),
    (POWERUP_SHIELD, CYAN, "S", "Shield Active!", 300),
    (POWERUP_REPAIR, GREEN, "R", "Repair!", 200),
]

# Obstacle types
OBSTACLE_OIL = "oil"
OBSTACLE_POTHOLE = "pothole"
OBSTACLE_BARRIER = "barrier"

OBSTACLE_TYPES = [
    (OBSTACLE_OIL, BROWN, "OIL", "Slow zone", 1.5),
    (OBSTACLE_POTHOLE, DARK_RED, "HOLE", "Damage", 1),
    (OBSTACLE_BARRIER, GRAY, "|||", "Stop", 2),
]

# Event types
EVENT_NITRO_BOOST = "nitro_boost"
EVENT_SPEED_BUMP = "speed_bump"
EVENT_MOVING_BARRIER = "moving_barrier"


class PlayerCar:
    """Player-controlled car - FIXED MOVEMENT"""
    
    WIDTH = 40
    HEIGHT = 60
    SPEED = 6
    
    def __init__(self, car_color=BLUE):
        self.x = SCREEN_WIDTH // 2 - self.WIDTH // 2
        self.y = SCREEN_HEIGHT - self.HEIGHT - 20
        self.rect = pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)
        self.color = car_color
        self.speed_multiplier = 1.0
        self.shield_active = False
        self.shield_timer = 0
        self.nitro_timer = 0
        
    def move_left(self):
        """Move left if within bounds"""
        if self.rect.left > ROAD_LEFT:
            self.rect.x -= self.SPEED
    
    def move_right(self):
        """Move right if within bounds"""
        if self.rect.right < ROAD_RIGHT:
            self.rect.x += self.SPEED
    
    def move_up(self):
        """Move up if within bounds"""
        if self.rect.top > 0:
            self.rect.y -= self.SPEED
    
    def move_down(self):
        """Move down if within bounds"""
        if self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.SPEED
    
    def get_lane(self):
        """Return current lane index (0, 1, 2)"""
        for i in range(LANE_COUNT):
            lane_center = ROAD_LEFT + LANE_WIDTH * i + LANE_WIDTH // 2
            if abs(self.rect.centerx - lane_center) < LANE_WIDTH // 2:
                return i
        return 1
    
    def apply_nitro(self, duration):
        self.speed_multiplier = 1.8
        self.nitro_timer = duration
    
    def apply_shield(self, duration):
        self.shield_active = True
        self.shield_timer = duration
    
    def update(self, dt):
        if self.nitro_timer > 0:
            self.nitro_timer -= dt
            if self.nitro_timer <= 0:
                self.speed_multiplier = 1.0
        
        if self.shield_timer > 0:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield_active = False
    
    def draw(self, surface):
        # Draw shield effect
        if self.shield_active:
            pygame.draw.circle(surface, CYAN, self.rect.center, self.WIDTH // 2 + 5, 3)
        
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (180, 220, 255),
                         (self.rect.x + 6, self.rect.y + 8, 28, 16),
                         border_radius=4)


class EnemyCar:
    """Traffic car that moves downwards"""
    
    WIDTH = 40
    HEIGHT = 60
    
    def __init__(self, speed, lane=None, color=None):
        if lane is None:
            lane = random.randint(0, LANE_COUNT - 1)
        
        lane_center = ROAD_LEFT + LANE_WIDTH * lane + LANE_WIDTH // 2
        self.rect = pygame.Rect(
            lane_center - self.WIDTH // 2,
            -self.HEIGHT,
            self.WIDTH,
            self.HEIGHT
        )
        self.speed = speed
        self.color = color or random.choice([RED, ORANGE, PURPLE])
        self.lane = lane
    
    def update(self):
        self.rect.y += self.speed
    
    def is_off_screen(self):
        return self.rect.top > SCREEN_HEIGHT
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        # Windows
        pygame.draw.rect(surface, (180, 220, 255),
                         (self.rect.x + 6, self.rect.y + 8, 28, 16),
                         border_radius=4)


class Obstacle:
    """Road obstacle (oil spill, pothole, barrier)"""
    
    SIZE = 25
    
    def __init__(self, obstacle_type, lane, speed):
        self.type = obstacle_type
        self.lane = lane
        lane_center = ROAD_LEFT + LANE_WIDTH * lane + LANE_WIDTH // 2
        
        for otype, color, symbol, effect, penalty in OBSTACLE_TYPES:
            if otype == obstacle_type:
                self.color = color
                self.symbol = symbol
                self.effect = effect
                self.penalty = penalty
                break
        
        self.rect = pygame.Rect(
            lane_center - self.SIZE // 2,
            -self.SIZE,
            self.SIZE,
            self.SIZE
        )
        self.speed = speed
    
    def update(self):
        self.rect.y += self.speed
    
    def is_off_screen(self):
        return self.rect.top > SCREEN_HEIGHT
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=4)
        if self.type == OBSTACLE_OIL:
            pygame.draw.ellipse(surface, (100, 50, 0), self.rect.inflate(-5, -5))
        elif self.type == OBSTACLE_POTHOLE:
            pygame.draw.circle(surface, BLACK, self.rect.center, self.SIZE // 3)
        else:
            for i in range(3):
                pygame.draw.line(surface, WHITE,
                                 (self.rect.x + 5, self.rect.y + i * 8),
                                 (self.rect.right - 5, self.rect.y + i * 8), 2)
        
        font = pygame.font.SysFont("Arial", 12, bold=True)
        text = font.render(self.symbol, True, WHITE)
        surface.blit(text, (self.rect.centerx - text.get_width() // 2,
                            self.rect.centery - text.get_height() // 2))


class DynamicEvent:
    """Dynamic road event"""
    
    def __init__(self, event_type, lane, y_pos=-100):
        self.type = event_type
        self.lane = lane
        lane_center = ROAD_LEFT + LANE_WIDTH * lane + LANE_WIDTH // 2
        
        if event_type == EVENT_NITRO_BOOST:
            self.width = 60
            self.height = 20
            self.color = (0, 255, 100)
            self.symbol = "BOOST"
        elif event_type == EVENT_SPEED_BUMP:
            self.width = 50
            self.height = 15
            self.color = (139, 69, 19)
            self.symbol = "BUMP"
        else:
            self.width = 30
            self.height = 30
            self.color = (100, 100, 100)
            self.symbol = "||"
        
        self.rect = pygame.Rect(
            lane_center - self.width // 2,
            y_pos,
            self.width,
            self.height
        )
        self.speed = 3
        self.direction = 1
    
    def update(self):
        self.rect.y += self.speed
        if self.type == EVENT_MOVING_BARRIER:
            self.rect.x += self.direction * 2
            if self.rect.left < ROAD_LEFT or self.rect.right > ROAD_RIGHT:
                self.direction *= -1
    
    def is_off_screen(self):
        return self.rect.top > SCREEN_HEIGHT
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=3)
        font = pygame.font.SysFont("Arial", 10, bold=True)
        text = font.render(self.symbol, True, WHITE)
        surface.blit(text, (self.rect.centerx - text.get_width() // 2,
                            self.rect.centery - text.get_height() // 2))


class PowerUp:
    """Collectible power-up"""
    
    SIZE = 25
    
    def __init__(self, powerup_type, lane, speed):
        self.type = powerup_type
        self.lane = lane
        lane_center = ROAD_LEFT + LANE_WIDTH * lane + LANE_WIDTH // 2
        
        for ptype, color, symbol, msg, duration in POWERUP_TYPES:
            if ptype == powerup_type:
                self.color = color
                self.symbol = symbol
                self.message = msg
                self.duration = duration
                break
        
        self.rect = pygame.Rect(
            lane_center - self.SIZE // 2,
            -self.SIZE,
            self.SIZE,
            self.SIZE
        )
        self.speed = speed
        self.lifetime = 300
        self.age = 0
    
    def update(self):
        self.rect.y += self.speed
        self.age += 1
    
    def is_off_screen(self):
        return self.rect.top > SCREEN_HEIGHT
    
    def expired(self):
        return self.age > self.lifetime
    
    def draw(self, surface):
        # Pulsing effect
        alpha = abs(math.sin(self.age * 0.05)) * 50 + 205
        pygame.draw.circle(surface, self.color, self.rect.center, self.SIZE // 2)
        pygame.draw.circle(surface, (255, 255, 255), self.rect.center, self.SIZE // 2, 2)
        
        font = pygame.font.SysFont("Arial", 14, bold=True)
        text = font.render(self.symbol, True, WHITE)
        surface.blit(text, (self.rect.centerx - text.get_width() // 2,
                            self.rect.centery - text.get_height() // 2))


class Coin:
    """Collectible coin with weighted value"""
    
    RADIUS = 10
    
    def __init__(self, lane, speed):
        self.lane = lane
        lane_center = ROAD_LEFT + LANE_WIDTH * lane + LANE_WIDTH // 2
        chosen = random.choices(COIN_TYPES, weights=_COIN_WEIGHTS, k=1)[0]
        _, self.value, self.body_color, self.outline_color, self.label = chosen
        
        self.center = [float(lane_center), float(-self.RADIUS)]
        self.rect = pygame.Rect(
            lane_center - self.RADIUS,
            -self.RADIUS * 2,
            self.RADIUS * 2,
            self.RADIUS * 2
        )
        self.speed = speed
    
    def update(self):
        self.center[1] += self.speed
        self.rect.center = (int(self.center[0]), int(self.center[1]))
    
    def is_off_screen(self):
        return self.center[1] > SCREEN_HEIGHT + self.RADIUS
    
    def draw(self, surface):
        cx, cy = int(self.center[0]), int(self.center[1])
        pygame.draw.circle(surface, self.body_color, (cx, cy), self.RADIUS)
        pygame.draw.circle(surface, self.outline_color, (cx, cy), self.RADIUS, 1)
        
        font = pygame.font.SysFont("Arial", 10, bold=True)
        text = font.render(self.label, True, self.outline_color)
        surface.blit(text, (cx - text.get_width() // 2, cy - text.get_height() // 2))


class Game:
    """Main game class"""
    
    def __init__(self, screen, username, settings):
        self.screen = screen
        self.username = username
        self.settings = settings
        
        # Game state
        self.running = True
        self.paused = False
        
        # Player
        self.player = PlayerCar(tuple(settings.get('car_color', BLUE)))
        
        # Score and progression
        self.score = 0
        self.distance = 0
        self.total_coins = 0
        self.distance_timer = 0
        
        # Speed and difficulty
        self.base_speed = 4
        self.current_speed = self.base_speed
        self.difficulty_multiplier = {
            'easy': 0.7,
            'medium': 1.0,
            'hard': 1.3
        }.get(settings.get('difficulty', 'medium'), 1.0)
        
        # Spawn timers
        self.enemy_timer = 0
        self.obstacle_timer = 0
        self.coin_timer = 0
        self.powerup_timer = 0
        self.event_timer = 0
        
        # Spawn intervals
        self.intervals = {
            'enemy': 90,
            'obstacle': 120,
            'coin': 45,
            'powerup': 300,
            'event': 400
        }
        
        # Game objects
        self.enemies = []
        self.obstacles = []
        self.coins = []
        self.powerups = []
        self.events = []
        
        # Active power-up
        self.active_powerup = None
        self.powerup_timer_active = 0
        self.powerup_message = ""
        self.message_timer = 0
        
        # Road scrolling
        self.road_offset = 0
        self.sound_on = settings.get('sound', True)
    
    def handle_events(self):
        """Handle keyboard input for movement"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                import sys
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                    self.set_message("PAUSED" if self.paused else "Resumed")
                if event.key == pygame.K_ESCAPE:
                    self.running = False
        
        # Continuous movement with key states
        keys = pygame.key.get_pressed()
        if not self.paused:
            if keys[pygame.K_LEFT]:
                self.player.move_left()
            if keys[pygame.K_RIGHT]:
                self.player.move_right()
            if keys[pygame.K_UP]:
                self.player.move_up()
            if keys[pygame.K_DOWN]:
                self.player.move_down()
    
    def update(self, dt):
        """Update game state"""
        if self.paused:
            return
        
        # Update current speed
        self.current_speed = self.base_speed * self.player.speed_multiplier
        self.current_speed *= self.difficulty_multiplier
        
        # Update distance and score
        self.distance_timer += self.current_speed * 0.1
        if self.distance_timer >= 1:
            self.distance += 1
            self.distance_timer = 0
            self.score += 1
        
        # Update player
        self.player.update(dt)
        
        # Update power-up timers
        if self.powerup_timer_active > 0:
            self.powerup_timer_active -= dt
            if self.powerup_timer_active <= 0:
                self.active_powerup = None
                self.player.speed_multiplier = 1.0
                self.player.shield_active = False
        
        if self.message_timer > 0:
            self.message_timer -= dt
        
        # Spawn objects (adjust intervals by difficulty)
        self.spawn_objects()
        
        # Update all objects
        self.update_enemies()
        self.update_obstacles()
        self.update_coins()
        self.update_powerups()
        self.update_events()
        
        # Check collisions
        self.check_collisions()
        
        # Update scrolling road
        self.road_offset = (self.road_offset + int(self.current_speed)) % 80
    
    def spawn_objects(self):
        """Spawn enemies, obstacles, coins, powerups, and events"""
        # Adjust spawn rate by difficulty
        spawn_mult = self.difficulty_multiplier
        
        # Spawn enemies
        self.enemy_timer += 1
        if self.enemy_timer >= int(self.intervals['enemy'] / spawn_mult):
            self.enemy_timer = 0
            # Avoid spawning directly on player
            player_lane = self.player.get_lane()
            lane = random.choice([l for l in range(LANE_COUNT) 
                                 if l != player_lane or random.random() > 0.5])
            self.enemies.append(EnemyCar(self.current_speed, lane))
        
        # Spawn obstacles
        self.obstacle_timer += 1
        if self.obstacle_timer >= int(self.intervals['obstacle'] / spawn_mult):
            self.obstacle_timer = 0
            lane = random.randint(0, LANE_COUNT - 1)
            obs_type = random.choice([OBSTACLE_OIL, OBSTACLE_POTHOLE, OBSTACLE_BARRIER])
            self.obstacles.append(Obstacle(obs_type, lane, self.current_speed))
        
        # Spawn coins
        self.coin_timer += 1
        if self.coin_timer >= self.intervals['coin']:
            self.coin_timer = 0
            lane = random.randint(0, LANE_COUNT - 1)
            self.coins.append(Coin(lane, self.current_speed))
        
        # Spawn power-ups
        self.powerup_timer += 1
        if self.powerup_timer >= self.intervals['powerup'] and len(self.powerups) < 2:
            self.powerup_timer = 0
            lane = random.randint(0, LANE_COUNT - 1)
            ptype = random.choice([POWERUP_NITRO, POWERUP_SHIELD, POWERUP_REPAIR])
            self.powerups.append(PowerUp(ptype, lane, self.current_speed))
        
        # Spawn dynamic events
        self.event_timer += 1
        if self.event_timer >= self.intervals['event']:
            self.event_timer = 0
            lane = random.randint(0, LANE_COUNT - 1)
            event_type = random.choice([EVENT_NITRO_BOOST, EVENT_SPEED_BUMP, EVENT_MOVING_BARRIER])
            self.events.append(DynamicEvent(event_type, lane))
    
    def update_enemies(self):
        for e in self.enemies[:]:
            e.update()
            if e.is_off_screen():
                self.enemies.remove(e)
    
    def update_obstacles(self):
        for o in self.obstacles[:]:
            o.update()
            if o.is_off_screen():
                self.obstacles.remove(o)
    
    def update_coins(self):
        for c in self.coins[:]:
            c.update()
            if c.is_off_screen():
                self.coins.remove(c)
    
    def update_powerups(self):
        for p in self.powerups[:]:
            p.update()
            if p.is_off_screen() or p.expired():
                self.powerups.remove(p)
    
    def update_events(self):
        for e in self.events[:]:
            e.update()
            if e.is_off_screen():
                self.events.remove(e)
    
    def check_collisions(self):
        """Check all collisions"""
        # Enemy collision
        for e in self.enemies:
            if self.player.rect.colliderect(e.rect):
                if self.player.shield_active:
                    self.player.shield_active = False
                    self.player.shield_timer = 0
                    self.set_message("Shield protected you!")
                    self.enemies.remove(e)
                else:
                    self.running = False
                return
        
        # Obstacle collision
        for o in self.obstacles:
            if self.player.rect.colliderect(o.rect):
                if o.type == OBSTACLE_OIL:
                    self.player.speed_multiplier = 0.5
                    self.set_message("Oil spill! Slowing down...")
                elif o.type == OBSTACLE_POTHOLE:
                    self.score = max(0, self.score - 50)
                    self.set_message("Pothole! -50 points")
                else:
                    self.set_message("Barrier! Stopped!")
                    self.player.speed_multiplier = 0.3
                self.obstacles.remove(o)
        
        # Coin collection
        for c in self.coins[:]:
            if self.player.rect.colliderect(c.rect):
                self.coins.remove(c)
                self.total_coins += c.value
                self.score += c.value * 10
                self.set_message(f"+{c.value} coins!")
        
        # Power-up collection
        for p in self.powerups[:]:
            if self.player.rect.colliderect(p.rect):
                self.powerups.remove(p)
                self.activate_powerup(p.type, p.duration)
                self.set_message(p.message)
        
        # Dynamic event collision
        for e in self.events[:]:
            if self.player.rect.colliderect(e.rect):
                if e.type == EVENT_NITRO_BOOST:
                    self.player.speed_multiplier = 2.0
                    self.set_message("Nitro Boost! Speed x2!")
                elif e.type == EVENT_SPEED_BUMP:
                    self.set_message("Speed bump!")
                    self.player.speed_multiplier = 0.7
                self.events.remove(e)
    
    def activate_powerup(self, powerup_type, duration):
        """Activate collected power-up"""
        self.active_powerup = powerup_type
        self.powerup_timer_active = duration
        
        if powerup_type == POWERUP_NITRO:
            self.player.speed_multiplier = 1.8
        elif powerup_type == POWERUP_SHIELD:
            self.player.shield_active = True
        elif powerup_type == POWERUP_REPAIR:
            if self.obstacles:
                self.obstacles.pop(0)
            self.player.speed_multiplier = 1.0
            self.player.shield_active = False
    
    def set_message(self, msg):
        """Show a temporary message"""
        self.powerup_message = msg
        self.message_timer = 60
    
    def draw(self):
        """Draw everything"""
        self.draw_road()
        
        for e in self.enemies:
            e.draw(self.screen)
        for o in self.obstacles:
            o.draw(self.screen)
        for c in self.coins:
            c.draw(self.screen)
        for p in self.powerups:
            p.draw(self.screen)
        for e in self.events:
            e.draw(self.screen)
        
        self.player.draw(self.screen)
        self.draw_hud()
        
        if self.message_timer > 0:
            font = pygame.font.SysFont("Arial", 18, bold=True)
            text = font.render(self.powerup_message, True, YELLOW)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 100))
            self.screen.blit(text, text_rect)
        
        if self.paused:
            self.draw_pause()
    
    def draw_road(self):
        """Draw scrolling road"""
        self.screen.fill((34, 120, 34))
        pygame.draw.rect(self.screen, GRAY,
                         (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, WHITE, (ROAD_LEFT, 0, 4, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, WHITE, (ROAD_RIGHT - 4, 0, 4, SCREEN_HEIGHT))
        
        # Lane markers
        for i in range(1, LANE_COUNT):
            lx = ROAD_LEFT + LANE_WIDTH * i
            for y in range(-40 + self.road_offset % 80, SCREEN_HEIGHT, 80):
                pygame.draw.rect(self.screen, WHITE, (lx - 2, y, 4, 30))
    
    def draw_hud(self):
        """Draw heads-up display"""
        font = pygame.font.SysFont("Arial", 18, bold=True)
        font_small = pygame.font.SysFont("Arial", 14)
        
        # Score and distance
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        dist_text = font.render(f"Distance: {int(self.distance)}m", True, WHITE)
        coin_text = font.render(f"Coins: {self.total_coins}", True, YELLOW)
        
        self.screen.blit(score_text, (8, 8))
        self.screen.blit(dist_text, (8, 30))
        self.screen.blit(coin_text, (8, 52))
        
        # Speed
        speed_text = font.render(f"Speed: {int(self.current_speed * 15)}km/h", True, WHITE)
        self.screen.blit(speed_text, (SCREEN_WIDTH - 120, 8))
        
        # Active power-up
        if self.active_powerup and self.powerup_timer_active > 0:
            time_left = int(self.powerup_timer_active / 60)
            power_text = font_small.render(f"{self.active_powerup}: {time_left}s", True, CYAN)
            self.screen.blit(power_text, (SCREEN_WIDTH - 130, 30))
        
        # Controls hint
        controls = font_small.render("← → ↑ ↓", True, GRAY)
        self.screen.blit(controls, (SCREEN_WIDTH - 80, 55))
    
    def draw_pause(self):
        """Draw pause screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        font_big = pygame.font.SysFont("Arial", 36, bold=True)
        font_small = pygame.font.SysFont("Arial", 18)
        
        pause_text = font_big.render("PAUSED", True, WHITE)
        resume_text = font_small.render("Press P to resume", True, WHITE)
        
        self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 250))
        self.screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, 320))