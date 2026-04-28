"""
Racer Game - TSIS3 Complete Edition
Fixed: Health system, Nitro boost with trail, No overlapping objects, Balanced difficulty
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
PINK = (255, 100, 150)

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
POWERUP_HEALTH = "health"

POWERUP_TYPES = [
    (POWERUP_NITRO, YELLOW, "N", "Nitro Boost!", 720),  # 3 seconds at 60fps
    (POWERUP_SHIELD, CYAN, "S", "Shield Active!", 900),
    (POWERUP_HEALTH, GREEN, "+", "+5 Health!", 0),
]

# Obstacle types with damage values
OBSTACLE_OIL = "oil"
OBSTACLE_POTHOLE = "pothole"
OBSTACLE_BARRIER = "barrier"

OBSTACLE_TYPES = [
    (OBSTACLE_OIL, BROWN, "OIL", "Oil spill", 2, 0.5),      # damage, speed reduction
    (OBSTACLE_POTHOLE, DARK_RED, "HOLE", "Pothole", 3, 1.0),
    (OBSTACLE_BARRIER, GRAY, "|||", "Barrier", 5, 0.3),
]


class PlayerCar:
    """Player-controlled car with health system"""
    
    WIDTH = 40
    HEIGHT = 60
    SPEED = 6
    MAX_HEALTH = 10
    
    def __init__(self, car_color=BLUE):
        self.x = SCREEN_WIDTH // 2 - self.WIDTH // 2
        self.y = SCREEN_HEIGHT - self.HEIGHT - 20
        self.rect = pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)
        self.color = car_color
        self.health = self.MAX_HEALTH
        self.speed_multiplier = 1.0
        self.shield_active = False
        self.shield_timer = 0
        self.nitro_active = False
        self.nitro_timer = 0
        self.nitro_trail = []  # For visual effect
        
    def move_left(self):
        if self.rect.left > ROAD_LEFT:
            self.rect.x -= self.SPEED
    
    def move_right(self):
        if self.rect.right < ROAD_RIGHT:
            self.rect.x += self.SPEED
    
    def move_up(self):
        if self.rect.top > 0:
            self.rect.y -= self.SPEED
    
    def move_down(self):
        if self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.SPEED
    
    def get_lane(self):
        for i in range(LANE_COUNT):
            lane_center = ROAD_LEFT + LANE_WIDTH * i + LANE_WIDTH // 2
            if abs(self.rect.centerx - lane_center) < LANE_WIDTH // 2:
                return i
        return 1
    
    def apply_nitro(self, duration):
        self.nitro_active = True
        self.nitro_timer = duration
        self.speed_multiplier = 2.0
    
    def apply_shield(self, duration):
        self.shield_active = True
        self.shield_timer = duration
    
    def apply_health(self, amount):
        self.health = min(self.MAX_HEALTH, self.health + amount)
    
    def take_damage(self, amount):
        if not self.shield_active:
            self.health -= amount
            return True  # Took damage
        return False  # Shield protected
    
    def update(self, dt):
        # Update nitro
        if self.nitro_timer > 0:
            self.nitro_timer -= dt
            # Add trail effect
            self.nitro_trail.append(self.rect.centerx)
            if len(self.nitro_trail) > 10:
                self.nitro_trail.pop(0)
            if self.nitro_timer <= 0:
                self.nitro_active = False
                self.speed_multiplier = 1.0
                self.nitro_trail.clear()
        else:
            self.nitro_active = False
        
        # Update shield
        if self.shield_timer > 0:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield_active = False
    
    def draw(self, surface):
        # Draw nitro trail
        if self.nitro_active and self.nitro_trail:
            for i, x_pos in enumerate(self.nitro_trail):
                alpha = int(255 * (i / len(self.nitro_trail)))
                trail_color = (255, 100, 0, alpha)
                pygame.draw.circle(surface, (255, 100, 0), 
                                 (int(x_pos), self.rect.bottom - i * 5), 5)
        
        # Draw shield effect
        if self.shield_active:
            pygame.draw.circle(surface, CYAN, self.rect.center, self.WIDTH // 2 + 5, 3)
        
        # Draw car body
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (180, 220, 255),
                         (self.rect.x + 6, self.rect.y + 8, 28, 16),
                         border_radius=4)
        
        # Draw nitro flames
        if self.nitro_active:
            pygame.draw.rect(surface, (255, 100, 0),
                           (self.rect.x + 10, self.rect.bottom - 5, 20, 8),
                           border_radius=3)


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
        pygame.draw.rect(surface, (180, 220, 255),
                         (self.rect.x + 6, self.rect.y + 8, 28, 16),
                         border_radius=4)


class Obstacle:
    """Road obstacle with damage"""
    
    SIZE = 25
    
    def __init__(self, obstacle_type, lane, speed):
        self.type = obstacle_type
        self.lane = lane
        lane_center = ROAD_LEFT + LANE_WIDTH * lane + LANE_WIDTH // 2
        
        for otype, color, symbol, effect, damage, speed_reduction in OBSTACLE_TYPES:
            if otype == obstacle_type:
                self.color = color
                self.symbol = symbol
                self.effect = effect
                self.damage = damage
                self.speed_reduction = speed_reduction
                break
        
        self.rect = pygame.Rect(
            lane_center - self.SIZE // 2,
            -self.SIZE,
            self.SIZE,
            self.SIZE
        )
        self.speed = speed
        self.active = True
    
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
        pulse = abs(math.sin(self.age * 0.05)) * 50 + 205
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
        
        # Spawn timers (increased intervals to reduce clutter)
        self.enemy_timer = 0
        self.obstacle_timer = 0
        self.coin_timer = 0
        self.powerup_timer = 0
        
        # Spawn intervals (slower spawning)
        self.intervals = {
            'enemy': 120,      # ~2 seconds at 60fps
            'obstacle': 180,   # ~3 seconds
            'coin': 60,        # ~1 second
            'powerup': 400,    # ~6.7 seconds
        }
        
        # Game objects
        self.enemies = []
        self.obstacles = []
        self.coins = []
        self.powerups = []
        
        # Track occupied lanes for spawning
        self.occupied_lanes = {'enemy': [], 'obstacle': [], 'coin': [], 'powerup': []}
        
        # Active power-up
        self.active_powerup = None
        self.powerup_timer_active = 0
        self.powerup_message = ""
        self.message_timer = 0
        
        # Road scrolling
        self.road_offset = 0
        self.sound_on = settings.get('sound', True)
        
        # Damage cooldown (prevent multiple damage from same obstacle)
        self.damage_cooldown = 0
        
        # Score multiplier based on distance
        self.score_multiplier = 1
    
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
        if self.paused or not self.running:
            return
        
        # Update damage cooldown
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt
        
        # Update current speed with difficulty
        self.current_speed = self.base_speed * self.player.speed_multiplier
        self.current_speed *= self.difficulty_multiplier
        self.current_speed = min(self.current_speed, 15)  # Cap speed
        
        # Update distance and score
        self.distance_timer += self.current_speed * 0.1
        if self.distance_timer >= 1:
            self.distance += 1
            self.distance_timer = 0
            # Score increases with distance
            score_gain = 1 * self.score_multiplier
            self.score += score_gain
            
            # Increase score multiplier every 500m
            if self.distance % 500 == 0 and self.distance > 0:
                self.score_multiplier += 0.5
                self.set_message(f"Score x{self.score_multiplier}!")
        
        # Update player
        self.player.update(dt)
        
        # Check game over condition
        if self.player.health <= 0:
            self.running = False
        
        # Update power-up timers
        if self.powerup_timer_active > 0:
            self.powerup_timer_active -= dt
            if self.powerup_timer_active <= 0:
                self.active_powerup = None
                if not self.player.nitro_active:
                    self.player.speed_multiplier = 1.0
                self.player.shield_active = False
        
        if self.message_timer > 0:
            self.message_timer -= dt
        
        # Spawn objects
        self.spawn_objects()
        
        # Update all objects
        self.update_enemies()
        self.update_obstacles()
        self.update_coins()
        self.update_powerups()
        
        # Check collisions
        self.check_collisions()
        
        # Update scrolling road
        self.road_offset = (self.road_offset + int(self.current_speed)) % 80
    
    def get_free_lane(self, object_type, exclude_lane=None):
        """Get a free lane for spawning, avoiding occupied lanes"""
        occupied = self.occupied_lanes.get(object_type, [])
        available = [l for l in range(LANE_COUNT) if l not in occupied]
        
        if exclude_lane is not None and exclude_lane in available:
            available.remove(exclude_lane)
        
        if available:
            return random.choice(available)
        return random.randint(0, LANE_COUNT - 1)
    
    def update_occupied_lanes(self):
        """Update which lanes are occupied by active objects"""
        self.occupied_lanes = {
            'enemy': [e.lane for e in self.enemies if e.rect.y < SCREEN_HEIGHT * 0.7],
            'obstacle': [o.lane for o in self.obstacles if o.rect.y < SCREEN_HEIGHT * 0.7],
            'coin': [c.lane for c in self.coins if c.rect.y < SCREEN_HEIGHT * 0.7],
            'powerup': [p.lane for p in self.powerups if p.rect.y < SCREEN_HEIGHT * 0.7],
        }
    
    def spawn_objects(self):
        """Spawn enemies, obstacles, coins, and powerups with lane management"""
        self.update_occupied_lanes()
        
        # Spawn enemies
        self.enemy_timer += 1
        if self.enemy_timer >= self.intervals['enemy']:
            self.enemy_timer = random.randint(-30, 0)  # Randomize timing
            lane = self.get_free_lane('enemy')
            self.enemies.append(EnemyCar(self.current_speed, lane))
        
        # Spawn obstacles (less frequent)
        self.obstacle_timer += 1
        if self.obstacle_timer >= self.intervals['obstacle']:
            self.obstacle_timer = random.randint(-20, 0)
            lane = self.get_free_lane('obstacle', self.player.get_lane())
            if random.random() < 0.7:  # 70% chance to spawn obstacle
                obs_type = random.choice([OBSTACLE_OIL, OBSTACLE_POTHOLE, OBSTACLE_BARRIER])
                self.obstacles.append(Obstacle(obs_type, lane, self.current_speed))
        
        # Spawn coins
        self.coin_timer += 1
        if self.coin_timer >= self.intervals['coin']:
            self.coin_timer = random.randint(-20, 0)
            lane = self.get_free_lane('coin')
            self.coins.append(Coin(lane, self.current_speed))
        
        # Spawn power-ups (rare)
        self.powerup_timer += 1
        if self.powerup_timer >= self.intervals['powerup']:
            self.powerup_timer = random.randint(-50, 0)
            lane = self.get_free_lane('powerup')
            ptype = random.choice([POWERUP_NITRO, POWERUP_SHIELD, POWERUP_HEALTH])
            self.powerups.append(PowerUp(ptype, lane, self.current_speed))
    
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
    
    def check_collisions(self):
        """Check all collisions with proper damage system"""
        # Enemy collision
        for e in self.enemies[:]:
            if self.player.rect.colliderect(e.rect):
                if self.player.take_damage(10):  # Enemy does 10 damage
                    self.set_message(f"CRASH! -10 HP! Health: {self.player.health}")
                    self.enemies.remove(e)
                    if self.player.health <= 0:
                        self.running = False
                        return
                else:
                    self.set_message("Shield blocked the crash!")
                    self.enemies.remove(e)
        
        # Obstacle collision with cooldown
        for o in self.obstacles[:]:
            if self.player.rect.colliderect(o.rect) and self.damage_cooldown <= 0:
                damage_taken = self.player.take_damage(o.damage)
                if damage_taken:
                    self.set_message(f"{o.effect}! -{o.damage} HP! Health: {self.player.health}")
                    # Apply speed reduction for oil
                    if o.type == OBSTACLE_OIL:
                        self.player.speed_multiplier = 0.5
                else:
                    self.set_message(f"Shield blocked {o.effect}!")
                
                self.obstacles.remove(o)
                self.damage_cooldown = 30  # 0.5 second cooldown at 60fps
                continue
        
        # Coin collection
        for c in self.coins[:]:
            if self.player.rect.colliderect(c.rect):
                self.coins.remove(c)
                self.total_coins += c.value
                self.score += c.value * 10
                self.set_message(f"+{c.value} coin!")
        
        # Power-up collection
        for p in self.powerups[:]:
            if self.player.rect.colliderect(p.rect):
                self.powerups.remove(p)
                self.activate_powerup(p.type, p.duration)
                self.set_message(p.message)
    
    def activate_powerup(self, powerup_type, duration):
        """Activate collected power-up"""
        self.active_powerup = powerup_type
        self.powerup_timer_active = duration
        
        if powerup_type == POWERUP_NITRO:
            self.player.apply_nitro(duration)
            self.set_message("NITRO BOOST! Speed x2!")
        elif powerup_type == POWERUP_SHIELD:
            self.player.apply_shield(duration)
            self.set_message("SHIELD ACTIVATED!")
        elif powerup_type == POWERUP_HEALTH:
            self.player.apply_health(5)
            self.set_message(f"+5 HEALTH! Health: {self.player.health}")
    
    def set_message(self, msg):
        """Show a temporary message"""
        self.powerup_message = msg
        self.message_timer = 240  # ← This controls message duration (60 frames = 1 second)
    
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
        
        self.player.draw(self.screen)
        self.draw_hud()
        
        if self.message_timer > 0:
            font = pygame.font.SysFont("Arial", 18, bold=True)
            text = font.render(self.powerup_message, True, YELLOW)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 100))
            # Draw background for text
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, BLACK, bg_rect)
            pygame.draw.rect(self.screen, YELLOW, bg_rect, 2)
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
        
        # Health bar
        health_width = 150
        health_height = 15
        health_x = 8
        health_y = 75
        health_percent = self.player.health / self.player.MAX_HEALTH
        
        pygame.draw.rect(self.screen, RED, (health_x, health_y, health_width, health_height))
        pygame.draw.rect(self.screen, GREEN, (health_x, health_y, health_width * health_percent, health_height))
        pygame.draw.rect(self.screen, WHITE, (health_x, health_y, health_width, health_height), 2)
        
        health_text = font_small.render(f"HP: {self.player.health}/{self.player.MAX_HEALTH}", True, WHITE)
        self.screen.blit(health_text, (health_x + 5, health_y - 12))
        
        # Score and distance
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        dist_text = font.render(f"Distance: {int(self.distance)}m", True, WHITE)
        coin_text = font.render(f"Coins: {self.total_coins}", True, YELLOW)
        multi_text = font_small.render(f"x{self.score_multiplier}", True, ORANGE)
        
        self.screen.blit(score_text, (8, 8))
        self.screen.blit(dist_text, (8, 30))
        self.screen.blit(coin_text, (8, 52))
        self.screen.blit(multi_text, (120, 8))
        
        # Speed
        speed_value = int(self.current_speed * 15)
        speed_text = font.render(f"Speed: {speed_value}km/h", True, WHITE)
        if self.player.nitro_active:
            speed_text = font.render(f"Speed: {speed_value}km/h", True, YELLOW)
        self.screen.blit(speed_text, (SCREEN_WIDTH - 130, 8))
        
        # Active power-up indicator
        if self.active_powerup and self.powerup_timer_active > 0:
            time_left = int(self.powerup_timer_active / 60) + 1
            color = YELLOW if self.active_powerup == POWERUP_NITRO else CYAN if self.active_powerup == POWERUP_SHIELD else GREEN
            power_text = font_small.render(f"{self.active_powerup.upper()}: {time_left}s", True, color)
            self.screen.blit(power_text, (SCREEN_WIDTH - 130, 30))
        
        # Controls hint
        controls = font_small.render("← → ↑ ↓  P:Pause", True, GRAY)
        self.screen.blit(controls, (SCREEN_WIDTH - 140, SCREEN_HEIGHT - 20))
    
    def draw_pause(self):
        """Draw pause screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        font_big = pygame.font.SysFont("Arial", 48, bold=True)
        font_small = pygame.font.SysFont("Arial", 18)
        
        pause_text = font_big.render("PAUSED", True, WHITE)
        resume_text = font_small.render("Press P to resume", True, WHITE)
        quit_text = font_small.render("Press ESC to quit", True, GRAY)
        
        self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 250))
        self.screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, 320))
        self.screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 350))