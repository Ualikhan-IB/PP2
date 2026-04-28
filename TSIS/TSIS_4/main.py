# main.py
import pygame
import sys
import json
import random
from config import *
from game import Snake, Food, PoisonFood, PowerUp, generate_obstacles, POWERUP_TYPES
from db import db

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game - TSIS4")
clock = pygame.time.Clock()

# Fonts
font_large = pygame.font.SysFont("Consolas", 40, bold=True)
font_medium = pygame.font.SysFont("Consolas", 24, bold=True)
font_small = pygame.font.SysFont("Consolas", 16)

# Load settings
def load_settings():
    try:
        with open("settings.json", "r") as f:
            return json.load(f)
    except:
        return {"snake_color": [50, 220, 50], "snake_body_color": [30, 160, 30], "grid_overlay": True, "sound_enabled": True}

def save_settings(settings_data):
    with open("settings.json", "w") as f:
        json.dump(settings_data, f, indent=2)

# Global settings variable
game_settings = load_settings()

# Screens
def draw_field(surface, obstacles, grid_enabled):
    pygame.draw.rect(surface, BG_COLOR, (0, PANEL_H, WIDTH, HEIGHT - PANEL_H))
    if grid_enabled:
        for col in range(COLS):
            for row in range(ROWS):
                px, py = col * CELL, row * CELL + PANEL_H
                pygame.draw.rect(surface, GRID_COLOR, (px, py, CELL, CELL), 1)
    for obs in obstacles:
        obs.draw(surface)
    pygame.draw.rect(surface, WALL_COLOR, (0, PANEL_H, WIDTH, ROWS * CELL), 3)

def draw_hud(surface, score, level, personal_best, active_powerup, powerup_time_left):
    pygame.draw.rect(surface, (20, 20, 40), (0, 0, WIDTH, PANEL_H))
    pygame.draw.line(surface, WALL_COLOR, (0, PANEL_H), (WIDTH, PANEL_H), 2)
    
    score_lbl = font_medium.render(f"Score: {score}", True, GOLD)
    surface.blit(score_lbl, (10, PANEL_H//2 - score_lbl.get_height()//2))
    
    level_lbl = font_medium.render(f"Level: {level}", True, BLUE)
    surface.blit(level_lbl, (WIDTH//2 - level_lbl.get_width()//2, PANEL_H//2 - level_lbl.get_height()//2))
    
    pb_lbl = font_small.render(f"Best: {personal_best}", True, (100, 255, 100))
    surface.blit(pb_lbl, (WIDTH - pb_lbl.get_width() - 10, PANEL_H//2 - pb_lbl.get_height()//2))
    
    if active_powerup and powerup_time_left > 0:
        pu_text = font_small.render(f"{active_powerup}: {powerup_time_left//1000}s", True, (255, 200, 0))
        surface.blit(pu_text, (WIDTH//2 - pu_text.get_width()//2, PANEL_H - 15))

def get_username():
    input_text = ""
    active = True
    while active:
        screen.fill(BG_COLOR)
        prompt = font_large.render("ENTER YOUR USERNAME", True, GOLD)
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 - 80))
        
        pygame.draw.rect(screen, (50, 50, 50), (WIDTH//2 - 150, HEIGHT//2, 300, 50), border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), (WIDTH//2 - 150, HEIGHT//2, 300, 50), 2, border_radius=5)
        text_surf = font_medium.render(input_text + "|", True, TEXT_COLOR)
        screen.blit(text_surf, (WIDTH//2 - 140, HEIGHT//2 + 12))
        
        instruction = font_small.render("Press ENTER to continue, ESC to quit", True, TEXT_COLOR)
        screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, HEIGHT//2 + 80))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                elif event.key == pygame.K_RETURN and input_text.strip():
                    return input_text.strip()
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.unicode.isprintable() and not event.unicode.isspace() and len(input_text) < 20:
                    input_text += event.unicode
        clock.tick(60)

def leaderboard_screen():
    while True:
        screen.fill(BG_COLOR)
        title = font_large.render("LEADERBOARD", True, GOLD)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        
        scores = db.get_top_scores(10)
        y = 100
        headers = ["Rank", "Username", "Score", "Level", "Date"]
        for i, h in enumerate(headers):
            txt = font_medium.render(h, True, BLUE)
            screen.blit(txt, (50 + i * 130, y))
        y += 40
        
        for idx, score in enumerate(scores):
            rank_txt = font_small.render(f"{idx+1}.", True, GOLD if idx < 3 else TEXT_COLOR)
            name_txt = font_small.render(score['username'][:15], True, TEXT_COLOR)
            score_txt = font_small.render(str(score['score']), True, TEXT_COLOR)
            level_txt = font_small.render(str(score['level_reached']), True, TEXT_COLOR)
            date_txt = font_small.render(score['played_at'].strftime("%Y-%m-%d"), True, (150,150,150))
            screen.blit(rank_txt, (55, y))
            screen.blit(name_txt, (120, y))
            screen.blit(score_txt, (255, y))
            screen.blit(level_txt, (365, y))
            screen.blit(date_txt, (450, y))
            y += 30
            if y > HEIGHT - 100:
                break
        
        back_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 80, 200, 50)
        pygame.draw.rect(screen, (50,50,50), back_rect, border_radius=5)
        pygame.draw.rect(screen, TEXT_COLOR, back_rect, 2, border_radius=5)
        back_text = font_medium.render("BACK", True, TEXT_COLOR)
        screen.blit(back_text, (back_rect.centerx - back_text.get_width()//2, back_rect.centery - back_text.get_height()//2))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_rect.collidepoint(event.pos):
                    return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
        clock.tick(60)

def settings_screen():
    global game_settings
    local_settings = game_settings.copy()
    r, g, b = local_settings["snake_color"]
    grid_on = local_settings["grid_overlay"]
    sound_on = local_settings["sound_enabled"]
    
    sliders = [
        {"label": "Red", "value": r, "rect": pygame.Rect(WIDTH//2 - 100, 150, 200, 10)},
        {"label": "Green", "value": g, "rect": pygame.Rect(WIDTH//2 - 100, 210, 200, 10)},
        {"label": "Blue", "value": b, "rect": pygame.Rect(WIDTH//2 - 100, 270, 200, 10)},
    ]
    dragging = [False, False, False]
    
    while True:
        screen.fill(BG_COLOR)
        title = font_large.render("SETTINGS", True, GOLD)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        
        # Grid toggle
        grid_rect = pygame.Rect(WIDTH//2 - 150, 350, 300, 50)
        pygame.draw.rect(screen, (50,50,50), grid_rect, border_radius=5)
        pygame.draw.rect(screen, TEXT_COLOR, grid_rect, 2, border_radius=5)
        grid_text = font_medium.render(f"Grid: {'ON' if grid_on else 'OFF'}", True, TEXT_COLOR)
        screen.blit(grid_text, (grid_rect.centerx - grid_text.get_width()//2, grid_rect.centery - grid_text.get_height()//2))
        
        # Sound toggle
        sound_rect = pygame.Rect(WIDTH//2 - 150, 420, 300, 50)
        pygame.draw.rect(screen, (50,50,50), sound_rect, border_radius=5)
        pygame.draw.rect(screen, TEXT_COLOR, sound_rect, 2, border_radius=5)
        sound_text = font_medium.render(f"Sound: {'ON' if sound_on else 'OFF'}", True, TEXT_COLOR)
        screen.blit(sound_text, (sound_rect.centerx - sound_text.get_width()//2, sound_rect.centery - sound_text.get_height()//2))
        
        # Color preview
        pygame.draw.rect(screen, (r,g,b), (WIDTH//2 + 120, 120, 60, 60))
        
        # Sliders
        for i, slider in enumerate(sliders):
            label = font_small.render(f"{slider['label']}: {slider['value']}", True, TEXT_COLOR)
            screen.blit(label, (WIDTH//2 - 180, slider['rect'].y - 5))
            pygame.draw.rect(screen, (50,50,50), slider['rect'], border_radius=5)
            fill_width = (slider['value'] / 255) * slider['rect'].width
            fill_rect = pygame.Rect(slider['rect'].x, slider['rect'].y, fill_width, slider['rect'].height)
            pygame.draw.rect(screen, (100,100,255), fill_rect, border_radius=5)
            handle_x = slider['rect'].x + fill_width - 5
            pygame.draw.circle(screen, (255,255,255), (int(handle_x), slider['rect'].centery), 8)
        
        # Save button
        save_rect = pygame.Rect(WIDTH//2 - 100, 510, 200, 50)
        pygame.draw.rect(screen, (0,100,0), save_rect, border_radius=5)
        pygame.draw.rect(screen, TEXT_COLOR, save_rect, 2, border_radius=5)
        save_text = font_medium.render("SAVE", True, TEXT_COLOR)
        screen.blit(save_text, (save_rect.centerx - save_text.get_width()//2, save_rect.centery - save_text.get_height()//2))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            
            # Mouse dragging for sliders
            for i, slider in enumerate(sliders):
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if slider['rect'].collidepoint(event.pos):
                        dragging[i] = True
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    dragging[i] = False
                elif event.type == pygame.MOUSEMOTION and dragging[i]:
                    x = max(slider['rect'].x, min(slider['rect'].x + slider['rect'].width, event.pos[0]))
                    slider['value'] = int((x - slider['rect'].x) / slider['rect'].width * 255)
                    r, g, b = sliders[0]['value'], sliders[1]['value'], sliders[2]['value']
            
            # Button clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if grid_rect.collidepoint(event.pos):
                    grid_on = not grid_on
                elif sound_rect.collidepoint(event.pos):
                    sound_on = not sound_on
                elif save_rect.collidepoint(event.pos):
                    game_settings["snake_color"] = [sliders[0]["value"], sliders[1]["value"], sliders[2]["value"]]
                    game_settings["grid_overlay"] = grid_on
                    game_settings["sound_enabled"] = sound_on
                    save_settings(game_settings)
                    return
        clock.tick(60)

def game_over_screen(score, level, personal_best):
    while True:
        screen.fill(BG_COLOR)
        go_text = font_large.render("GAME OVER", True, RED)
        screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, 80))
        
        score_text = font_medium.render(f"Score: {score}", True, GOLD)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 180))
        
        level_text = font_medium.render(f"Level: {level}", True, BLUE)
        screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, 230))
        
        pb_text = font_medium.render(f"Personal Best: {personal_best}", True, (100,255,100))
        screen.blit(pb_text, (WIDTH//2 - pb_text.get_width()//2, 280))
        
        retry_rect = pygame.Rect(WIDTH//2 - 220, HEIGHT - 120, 200, 50)
        menu_rect = pygame.Rect(WIDTH//2 + 20, HEIGHT - 120, 200, 50)
        
        pygame.draw.rect(screen, (0,100,0), retry_rect, border_radius=5)
        pygame.draw.rect(screen, (100,100,0), menu_rect, border_radius=5)
        pygame.draw.rect(screen, TEXT_COLOR, retry_rect, 2, border_radius=5)
        pygame.draw.rect(screen, TEXT_COLOR, menu_rect, 2, border_radius=5)
        
        retry_text = font_medium.render("RETRY", True, TEXT_COLOR)
        menu_text = font_medium.render("MENU", True, TEXT_COLOR)
        screen.blit(retry_text, (retry_rect.centerx - retry_text.get_width()//2, retry_rect.centery - retry_text.get_height()//2))
        screen.blit(menu_text, (menu_rect.centerx - menu_text.get_width()//2, menu_rect.centery - menu_text.get_height()//2))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if retry_rect.collidepoint(event.pos):
                    return True
                if menu_rect.collidepoint(event.pos):
                    return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
        clock.tick(60)

def main_menu():
    while True:
        screen.fill(BG_COLOR)
        title = font_large.render("SNAKE GAME", True, GOLD)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        buttons = [
            ("PLAY", WIDTH//2 - 100, 150, 200, 50, (0,100,0)),
            ("LEADERBOARD", WIDTH//2 - 100, 230, 200, 50, (0,0,100)),
            ("SETTINGS", WIDTH//2 - 100, 310, 200, 50, (100,100,0)),
            ("QUIT", WIDTH//2 - 100, 390, 200, 50, (100,0,0)),
        ]
        
        rects = []
        for text, x, y, w, h, color in buttons:
            rect = pygame.Rect(x, y, w, h)
            pygame.draw.rect(screen, color, rect, border_radius=5)
            pygame.draw.rect(screen, TEXT_COLOR, rect, 2, border_radius=5)
            btn_text = font_medium.render(text, True, TEXT_COLOR)
            screen.blit(btn_text, (rect.centerx - btn_text.get_width()//2, rect.centery - btn_text.get_height()//2))
            rects.append((rect, text))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, text in rects:
                    if rect.collidepoint(event.pos):
                        if text == "PLAY":
                            return
                        elif text == "LEADERBOARD":
                            leaderboard_screen()
                        elif text == "SETTINGS":
                            settings_screen()
                        elif text == "QUIT":
                            pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
        clock.tick(60)

def game_loop(username):
    player_id = db.get_or_create_player(username)
    personal_best = db.get_personal_best(player_id)
    
    snake = Snake()
    food = Food()
    poison = PoisonFood()
    powerups = [PowerUp(p[0], p[1], p[2]) for p in POWERUP_TYPES]
    
    food.respawn(snake.body)
    
    score = 0
    level = 1
    food_eaten = 0
    move_delay = BASE_MOVE
    frame_count = 0
    
    obstacles = []
    active_powerup = None
    powerup_end_time = 0
    last_powerup_spawn = pygame.time.get_ticks()
    last_poison_spawn = pygame.time.get_ticks()
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        frame_count += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w): snake.set_direction(0, -1)
                if event.key in (pygame.K_DOWN, pygame.K_s): snake.set_direction(0, 1)
                if event.key in (pygame.K_LEFT, pygame.K_a): snake.set_direction(-1, 0)
                if event.key in (pygame.K_RIGHT, pygame.K_d): snake.set_direction(1, 0)
        
        snake.update_shield(current_time)
        
        # Power-up expiration
        if active_powerup and current_time >= powerup_end_time:
            if active_powerup == "speed_boost":
                move_delay = BASE_MOVE
            elif active_powerup == "slow_motion":
                move_delay = BASE_MOVE
            active_powerup = None
        
        # Spawn power-ups
        powerup_active = any(p.active for p in powerups)
        if not powerup_active and current_time - last_powerup_spawn > 5000:
            occupied = set()
            if not food.expired(current_time):
                occupied.add(food.pos)
            if poison.active and not poison.expired(current_time):
                occupied.add(poison.pos)
            for pu in powerups:
                if not pu.active and pu.spawn_at_free_cell(snake.body, occupied, [obs.pos for obs in obstacles]):
                    last_powerup_spawn = current_time
                    break
        
        # Spawn poison
        if not poison.active and random.random() < 0.02 and current_time - last_poison_spawn > 5000:
            if poison.spawn(snake.body, [obs.pos for obs in obstacles]):
                last_poison_spawn = current_time
        
        # Movement
        if frame_count % move_delay == 0:
            current_head = snake.body[0]
            
            if level >= OBSTACLES_FROM_LEVEL and not obstacles:
                obstacles = generate_obstacles(level, snake.body, current_head)
            
            if not snake.step([obs.pos for obs in obstacles]):
                db.save_game_result(player_id, score, level)
                return game_over_screen(score, level, personal_best)
            
            new_head = snake.body[0]
            
            # Food
            if new_head == food.pos and not food.expired(current_time):
                score += food.points
                food_eaten += 1
                snake.grow()
                food.respawn(snake.body, [obs.pos for obs in obstacles])
                if food_eaten >= FOOD_PER_LEVEL:
                    level += 1
                    food_eaten = 0
                    move_delay = max(3, BASE_MOVE - min(5, level - 1))
                    obstacles = generate_obstacles(level, snake.body, new_head)
            
            # Poison
            if poison.active and not poison.expired(current_time) and new_head == poison.pos:
                if snake.shorten(2):
                    db.save_game_result(player_id, score, level)
                    return game_over_screen(score, level, personal_best)
                poison.active = False
                score = max(0, score - 2)
            
            # Power-ups
            for pu in powerups:
                if pu.active and not pu.expired(current_time) and new_head == pu.pos:
                    pu.active = False
                    active_powerup = pu.type
                    powerup_end_time = current_time + POWERUP_DURATION
                    if pu.type == "speed_boost":
                        move_delay = max(3, move_delay - 3)
                    elif pu.type == "slow_motion":
                        move_delay = min(15, move_delay + 3)
                    elif pu.type == "shield":
                        snake.set_shield(POWERUP_DURATION, current_time)
        
        # Cleanup expired items
        for pu in powerups:
            if pu.active and pu.expired(current_time):
                pu.active = False
        if food.expired(current_time):
            food.respawn(snake.body, [obs.pos for obs in obstacles])
        if poison.active and poison.expired(current_time):
            poison.active = False
        
        # Draw
        draw_field(screen, obstacles, game_settings["grid_overlay"])
        food.draw(screen, current_time, font_small)
        poison.draw(screen, current_time, font_small)
        for pu in powerups:
            pu.draw(screen, current_time, font_small)
        snake.draw(screen, tuple(game_settings["snake_color"]), tuple(game_settings["snake_body_color"]))
        
        powerup_time_left = max(0, powerup_end_time - current_time) if active_powerup else 0
        draw_hud(screen, score, level, personal_best, active_powerup, powerup_time_left)
        
        if snake.shield_active:
            shield_text = font_small.render("SHIELD ACTIVE", True, (255,200,0))
            screen.blit(shield_text, (10, PANEL_H - 15))
        
        pygame.display.flip()
        clock.tick(BASE_FPS)
    
    return True

def main():
    while True:
        main_menu()
        username = get_username()
        retry = game_loop(username)
        if not retry:
            continue

if __name__ == "__main__":
    main()