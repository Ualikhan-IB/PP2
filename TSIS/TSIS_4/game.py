# game.py
import pygame
import sys
import random
from config import *
from db import db

def cell_to_px(col, row):
    return col * CELL, row * CELL + PANEL_H

class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        cx, cy = COLS // 2, ROWS // 2
        self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.next_dir = (1, 0)
        self.grew = False
        self.shield_active = False
        self.shield_until = 0
        self.slow_until = 0
        self.original_move_delay = 0
    
    def set_direction(self, dx, dy):
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.next_dir = (dx, dy)
    
    def step(self, obstacles=None):
        self.direction = self.next_dir
        hx, hy = self.body[0]
        new_head = (hx + self.direction[0], hy + self.direction[1])
        
        # Wall collision
        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            if self.shield_active:
                self.shield_active = False
                return True
            return False
        
        # Obstacle collision
        if obstacles and new_head in obstacles:
            if self.shield_active:
                self.shield_active = False
                return True
            return False
        
        # Self collision
        if new_head in self.body:
            if self.shield_active:
                self.shield_active = False
                return True
            return False
        
        self.body.insert(0, new_head)
        if self.grew:
            self.grew = False
        else:
            self.body.pop()
        return True
    
    def grow(self):
        self.grew = True
    
    def shorten(self, segments=2):
        for _ in range(min(segments, len(self.body) - 1)):
            self.body.pop()
        return len(self.body) <= 0
    
    def set_shield(self, duration_ms, current_time):
        self.shield_active = True
        self.shield_until = current_time + duration_ms
    
    def update_shield(self, current_time):
        if self.shield_active and current_time >= self.shield_until:
            self.shield_active = False
    
    def draw(self, surface, snake_color, snake_body_color):
        for i, (col, row) in enumerate(self.body):
            px, py = cell_to_px(col, row)
            color = snake_color if i == 0 else snake_body_color
            pygame.draw.rect(surface, color, (px+1, py+1, CELL-2, CELL-2), border_radius=4)
            pygame.draw.rect(surface, SNAKE_OUTLINE, (px+1, py+1, CELL-2, CELL-2), 1, border_radius=4)
        
        # Draw shield effect if active
        if self.shield_active:
            head_col, head_row = self.body[0]
            px, py = cell_to_px(head_col, head_row)
            cx, cy = px + CELL // 2, py + CELL // 2
            pygame.draw.circle(surface, (100, 200, 255), (cx, cy), CELL // 2 + 2, 3)
            pygame.draw.circle(surface, (150, 220, 255), (cx, cy), CELL // 2 + 4, 1)

class Food:
    def __init__(self):
        self.pos = (0, 0)
        self.points = 1
        self.color = (220, 50, 50)
        self.shine = (255, 120, 120)
        self.spawn_time = 0
    
    def respawn(self, snake_body, obstacles=None):
        free = [(c, r) for c in range(COLS) for r in range(ROWS)
                if (c, r) not in snake_body and (not obstacles or (c, r) not in obstacles)]
        if not free:
            return False
        
        self.pos = random.choice(free)
        chosen = random.choices(FOOD_TYPES, weights=[ft[0] for ft in FOOD_TYPES], k=1)[0]
        _, self.points, self.color, self.shine, _ = chosen
        self.spawn_time = pygame.time.get_ticks()
        return True
    
    def expired(self, current_time):
        return current_time - self.spawn_time >= FOOD_LIFETIME
    
    def time_frac(self, current_time):
        remaining = max(0, FOOD_LIFETIME - (current_time - self.spawn_time))
        return remaining / FOOD_LIFETIME
    
    def draw(self, surface, current_time, font_small):
        if self.expired(current_time):
            return
        
        col, row = self.pos
        px, py = cell_to_px(col, row)
        cx, cy = px + CELL // 2, py + CELL // 2
        r = CELL // 2 - 2
        
        pygame.draw.circle(surface, self.color, (cx, cy), r)
        pygame.draw.circle(surface, self.shine, (cx-3, cy-3), 4)
        
        lbl = font_small.render(f"+{self.points}", True, TEXT_COLOR)
        surface.blit(lbl, (cx - lbl.get_width()//2, cy - lbl.get_height()//2))
        
        # Timer bar
        frac = self.time_frac(current_time)
        bar_col = (50, 210, 50) if frac > 0.5 else (255, 200, 0) if frac > 0.25 else (210, 40, 40)
        bar_x, bar_y = px, py + CELL + BAR_PAD
        pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, CELL, BAR_H), border_radius=3)
        pygame.draw.rect(surface, bar_col, (bar_x, bar_y, max(1, int(CELL * frac)), BAR_H), border_radius=3)

class PoisonFood:
    def __init__(self):
        self.pos = (0, 0)
        self.active = False
        self.spawn_time = 0
    
    def spawn(self, snake_body, obstacles=None):
        free = [(c, r) for c in range(COLS) for r in range(ROWS)
                if (c, r) not in snake_body and (not obstacles or (c, r) not in obstacles)]
        if free and not self.active:
            self.pos = random.choice(free)
            self.active = True
            self.spawn_time = pygame.time.get_ticks()
            return True
        return False
    
    def expired(self, current_time):
        return current_time - self.spawn_time >= FOOD_LIFETIME
    
    def draw(self, surface, current_time, font_small):
        if not self.active or self.expired(current_time):
            return
        col, row = self.pos
        px, py = cell_to_px(col, row)
        cx, cy = px + CELL // 2, py + CELL // 2
        pygame.draw.circle(surface, DARK_RED, (cx, cy), CELL // 2 - 2)
        pygame.draw.line(surface, (50, 50, 50), (cx-5, cy-5), (cx+5, cy+5), 2)
        pygame.draw.line(surface, (50, 50, 50), (cx+5, cy-5), (cx-5, cy+5), 2)
        lbl = font_small.render("-2", True, TEXT_COLOR)
        surface.blit(lbl, (cx - lbl.get_width()//2, cy - lbl.get_height()//2))

class SlowField:
    """Sludge/Slow field that slows down the snake when touched"""
    def __init__(self):
        self.pos = (0, 0)
        self.active = False
        self.spawn_time = 0
    
    def spawn(self, snake_body, obstacles=None):
        free = [(c, r) for c in range(COLS) for r in range(ROWS)
                if (c, r) not in snake_body and (not obstacles or (c, r) not in obstacles)]
        if free and not self.active:
            self.pos = random.choice(free)
            self.active = True
            self.spawn_time = pygame.time.get_ticks()
            return True
        return False
    
    def expired(self, current_time):
        return current_time - self.spawn_time >= FOOD_LIFETIME
    
    def draw(self, surface, current_time, font_small):
        if not self.active or self.expired(current_time):
            return
        col, row = self.pos
        px, py = cell_to_px(col, row)
        cx, cy = px + CELL // 2, py + CELL // 2
        
        # Draw purple sludge/goo effect
        pygame.draw.circle(surface, (128, 0, 128), (cx, cy), CELL // 2 - 2)
        pygame.draw.circle(surface, (180, 50, 180), (cx-2, cy-2), 4)
        
        # Draw snail/slow symbol
        lbl = font_small.render("🐌", True, TEXT_COLOR)
        surface.blit(lbl, (cx - lbl.get_width()//2, cy - lbl.get_height()//2))
        
        # Timer bar
        remaining = (FOOD_LIFETIME - (current_time - self.spawn_time)) / FOOD_LIFETIME
        bar_x, bar_y = px, py + CELL + BAR_PAD
        bar_col = (255, 165, 0)
        pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, CELL, BAR_H), border_radius=3)
        pygame.draw.rect(surface, bar_col, (bar_x, bar_y, max(1, int(CELL * remaining)), BAR_H), border_radius=3)

class PowerUp:
    def __init__(self, power_type, color, symbol):
        self.type = power_type
        self.color = color
        self.symbol = symbol
        self.pos = (0, 0)
        self.active = False
        self.spawn_time = 0
    
    def spawn_at_free_cell(self, snake_body, occupied, obstacles=None):
        all_occupied = set(snake_body) | occupied
        if obstacles:
            all_occupied |= set(obstacles)
        free = [(c, r) for c in range(COLS) for r in range(ROWS) if (c, r) not in all_occupied]
        if free and not self.active:
            self.pos = random.choice(free)
            self.active = True
            self.spawn_time = pygame.time.get_ticks()
            return True
        return False
    
    def expired(self, current_time):
        return current_time - self.spawn_time >= POWERUP_LIFETIME
    
    def draw(self, surface, current_time, font_small):
        if not self.active or self.expired(current_time):
            return
        col, row = self.pos
        px, py = cell_to_px(col, row)
        cx, cy = px + CELL // 2, py + CELL // 2
        pygame.draw.polygon(surface, self.color, [
            (cx, cy-6), (cx+3, cy-2), (cx+7, cy-2), (cx+4, cy+2),
            (cx+5, cy+7), (cx, cy+4), (cx-5, cy+7), (cx-4, cy+2),
            (cx-7, cy-2), (cx-3, cy-2)])
        sym = font_small.render(self.symbol, True, TEXT_COLOR)
        surface.blit(sym, (cx - sym.get_width()//2, cy-5))

class Obstacle:
    def __init__(self, pos):
        self.pos = pos
    
    def draw(self, surface):
        col, row = self.pos
        px, py = cell_to_px(col, row)
        pygame.draw.rect(surface, (139, 69, 19), (px, py, CELL, CELL))
        pygame.draw.rect(surface, (100, 50, 0), (px, py, CELL, CELL), 2)

def generate_obstacles(level, snake_body, current_head):
    if level < OBSTACLES_FROM_LEVEL:
        return []
    
    num_obstacles = min(5 + (level - OBSTACLES_FROM_LEVEL), ROWS * COLS // 8)
    occupied = set(snake_body)
    obstacles = []
    attempts = 0
    
    while len(obstacles) < num_obstacles and attempts < 100:
        col, row = random.randint(0, COLS-1), random.randint(0, ROWS-1)
        pos = (col, row)
        if pos not in occupied and abs(col - current_head[0]) + abs(row - current_head[1]) > 2:
            obstacles.append(Obstacle(pos))
            occupied.add(pos)
        attempts += 1
    return obstacles