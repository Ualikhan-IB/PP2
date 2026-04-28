"""
UI Screens - Fixed event handling
"""

import pygame
import sys

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK = (50, 50, 50)
RED = (220, 30, 30)
GREEN = (30, 200, 30)
BLUE = (30, 100, 220)
YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)


class Button:
    """Simple UI Button"""
    
    def __init__(self, x, y, width, height, text, color=BLUE, hover_color=GREEN):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
    
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
    
    def draw(self, surface, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click


class MainMenu:
    """Main menu screen"""
    
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont("Arial", 48, bold=True)
        self.font = pygame.font.SysFont("Arial", 28)
        
        button_width, button_height = 200, 50
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        
        self.buttons = {
            'play': Button(button_x, 250, button_width, button_height, "PLAY"),
            'leaderboard': Button(button_x, 320, button_width, button_height, "LEADERBOARD"),
            'settings': Button(button_x, 390, button_width, button_height, "SETTINGS"),
            'quit': Button(button_x, 460, button_width, button_height, "QUIT", RED),
        }
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True
        
        for key, button in self.buttons.items():
            button.update(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_click):
                return key
        
        return None
    
    def draw(self):
        self.screen.fill(DARK)
        
        title = self.font_title.render("RACER", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title, title_rect)
        
        font_small = pygame.font.SysFont("Arial", 16)
        subtitle = font_small.render("TSIS3 - Ultimate Racing", True, GRAY)
        sub_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 170))
        self.screen.blit(subtitle, sub_rect)
        
        for button in self.buttons.values():
            button.draw(self.screen, self.font)


class UsernamePrompt:
    """Username input screen"""
    
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont("Arial", 32, bold=True)
        self.font = pygame.font.SysFont("Arial", 24)
        
        self.username = ""
        self.active = True
        
        button_width, button_height = 120, 40
        self.buttons = {
            'play': Button(SCREEN_WIDTH // 2 - button_width - 10, 400, button_width, button_height, "PLAY", GREEN),
            'back': Button(SCREEN_WIDTH // 2 + 10, 400, button_width, button_height, "BACK", RED),
        }
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.username:
                    return self.username, "play"
                elif event.key == pygame.K_BACKSPACE:
                    self.username = self.username[:-1]
                elif event.unicode and event.unicode.isprintable() and len(self.username) < 20:
                    self.username += event.unicode
        
        for key, button in self.buttons.items():
            button.update(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_click):
                return self.username, key
        
        return self.username, None
    
    def draw(self):
        self.screen.fill(DARK)
        
        title = self.font_title.render("ENTER YOUR NAME", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 200, 300, 50)
        pygame.draw.rect(self.screen, WHITE, input_rect, border_radius=8)
        pygame.draw.rect(self.screen, BLUE, input_rect, 3, border_radius=8)
        
        name_text = self.font.render(self.username or "_", True, BLACK)
        name_rect = name_text.get_rect(center=input_rect.center)
        self.screen.blit(name_text, name_rect)
        
        instr = pygame.font.SysFont("Arial", 14).render("Press ENTER to continue", True, GRAY)
        instr_rect = instr.get_rect(center=(SCREEN_WIDTH // 2, 280))
        self.screen.blit(instr, instr_rect)
        
        for button in self.buttons.values():
            button.draw(self.screen, self.font)


class LeaderboardScreen:
    """Leaderboard display screen"""
    
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_header = pygame.font.SysFont("Arial", 18, bold=True)
        self.font = pygame.font.SysFont("Arial", 16)
        
        self.back_button = Button(SCREEN_WIDTH // 2 - 50, 520, 100, 40, "BACK", BLUE, ORANGE)
        self.leaderboard = []
        self.refresh()
    
    def refresh(self):
        from persistence import load_leaderboard
        self.leaderboard = load_leaderboard()[:10]
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True
        
        self.back_button.update(mouse_pos)
        if self.back_button.is_clicked(mouse_pos, mouse_click):
            return "back"
        
        return None
    
    def draw(self):
        self.screen.fill(DARK)
        
        title = self.font_title.render("TOP 10 RACERS", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        headers = ["#", "NAME", "SCORE", "DIST", "COINS"]
        x_positions = [30, 80, 220, 300, 360]
        
        for i, header in enumerate(headers):
            text = self.font_header.render(header, True, ORANGE)
            self.screen.blit(text, (x_positions[i], 100))
        
        pygame.draw.line(self.screen, GRAY, (20, 125), (SCREEN_WIDTH - 20, 125), 2)
        
        y = 140
        for i, entry in enumerate(self.leaderboard):
            color = YELLOW if i < 3 else WHITE
            rank = f"{i + 1}"
            name = entry.get('name', 'Unknown')[:12]
            score = str(entry.get('score', 0))
            distance = str(int(entry.get('distance', 0)))
            coins = str(entry.get('coins', 0))
            
            values = [rank, name, score, distance, coins]
            for j, val in enumerate(values):
                text = self.font.render(val, True, color)
                self.screen.blit(text, (x_positions[j], y))
            
            y += 25
            if y > 500:
                break
        
        self.back_button.draw(self.screen, self.font)


class SettingsScreen:
    """Settings screen"""
    
    def __init__(self, screen, current_settings):
        self.screen = screen
        self.font_title = pygame.font.SysFont("Arial", 32, bold=True)
        self.font = pygame.font.SysFont("Arial", 20)
        
        self.settings = current_settings.copy()
        
        self.difficulties = ['easy', 'medium', 'hard']
        self.car_colors = [
            ('BLUE', (30, 100, 220)),
            ('RED', (220, 30, 30)),
            ('GREEN', (30, 200, 30)),
            ('PURPLE', (160, 32, 240))
        ]
        
        self.difficulty_index = self.difficulties.index(self.settings.get('difficulty', 'medium'))
        self.car_color_index = 0
        for i, (name, color) in enumerate(self.car_colors):
            if color == tuple(self.settings.get('car_color', (30, 100, 220))):
                self.car_color_index = i
                break
        
        button_width = 120
        self.save_button = Button(SCREEN_WIDTH // 2 - button_width - 10, 520, button_width, 40, "SAVE", GREEN)
        self.back_button = Button(SCREEN_WIDTH // 2 + 10, 520, button_width, 40, "BACK", BLUE)
        
        self.sound_on = self.settings.get('sound', True)
    
    def refresh(self):
        """Refresh settings from file"""
        from persistence import load_settings
        self.settings = load_settings()
        self.difficulty_index = self.difficulties.index(self.settings.get('difficulty', 'medium'))
        self.sound_on = self.settings.get('sound', True)
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.difficulty_index = (self.difficulty_index - 1) % len(self.difficulties)
                elif event.key == pygame.K_RIGHT:
                    self.difficulty_index = (self.difficulty_index + 1) % len(self.difficulties)
        
        self.save_button.update(mouse_pos)
        self.back_button.update(mouse_pos)
        
        # Sound toggle
        sound_rect = pygame.Rect(SCREEN_WIDTH // 2 - 30, 300, 60, 30)
        if sound_rect.collidepoint(mouse_pos) and mouse_click:
            self.sound_on = not self.sound_on
        
        # Color selection
        for i in range(len(self.car_colors)):
            color_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100 + i * 50, 380, 40, 40)
            if color_rect.collidepoint(mouse_pos) and mouse_click:
                self.car_color_index = i
        
        # Difficulty arrows
        left_arrow = pygame.Rect(SCREEN_WIDTH // 2 - 80, 240, 30, 30)
        right_arrow = pygame.Rect(SCREEN_WIDTH // 2 + 50, 240, 30, 30)
        if left_arrow.collidepoint(mouse_pos) and mouse_click:
            self.difficulty_index = (self.difficulty_index - 1) % len(self.difficulties)
        if right_arrow.collidepoint(mouse_pos) and mouse_click:
            self.difficulty_index = (self.difficulty_index + 1) % len(self.difficulties)
        
        if self.save_button.is_clicked(mouse_pos, mouse_click):
            self.settings['difficulty'] = self.difficulties[self.difficulty_index]
            self.settings['car_color'] = self.car_colors[self.car_color_index][1]
            self.settings['sound'] = self.sound_on
            return "save", self.settings
        
        if self.back_button.is_clicked(mouse_pos, mouse_click):
            return "back", self.settings
        
        return None, self.settings
    
    def draw(self):
        self.screen.fill(DARK)
        
        title = self.font_title.render("SETTINGS", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Difficulty
        diff_label = self.font.render("Difficulty:", True, WHITE)
        self.screen.blit(diff_label, (SCREEN_WIDTH // 2 - 80, 210))
        
        pygame.draw.polygon(self.screen, WHITE, 
                           [(SCREEN_WIDTH // 2 - 70, 250), 
                            (SCREEN_WIDTH // 2 - 85, 265), 
                            (SCREEN_WIDTH // 2 - 70, 280)])
        
        diff_text = self.font.render(self.difficulties[self.difficulty_index].upper(), True, ORANGE)
        diff_rect = diff_text.get_rect(center=(SCREEN_WIDTH // 2, 265))
        self.screen.blit(diff_text, diff_rect)
        
        pygame.draw.polygon(self.screen, WHITE,
                           [(SCREEN_WIDTH // 2 + 70, 250),
                            (SCREEN_WIDTH // 2 + 85, 265),
                            (SCREEN_WIDTH // 2 + 70, 280)])
        
        # Sound
        sound_label = self.font.render("Sound:", True, WHITE)
        self.screen.blit(sound_label, (SCREEN_WIDTH // 2 - 80, 310))
        
        sound_rect = pygame.Rect(SCREEN_WIDTH // 2 - 30, 300, 60, 30)
        pygame.draw.rect(self.screen, GREEN if self.sound_on else RED, sound_rect, border_radius=5)
        sound_text = self.font.render("ON" if self.sound_on else "OFF", True, WHITE)
        sound_rect_text = sound_text.get_rect(center=sound_rect.center)
        self.screen.blit(sound_text, sound_rect_text)
        
        # Car Color
        color_label = self.font.render("Car Color:", True, WHITE)
        self.screen.blit(color_label, (SCREEN_WIDTH // 2 - 80, 390))
        
        for i, (name, color) in enumerate(self.car_colors):
            color_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100 + i * 50, 380, 40, 40)
            pygame.draw.rect(self.screen, color, color_rect, border_radius=5)
            if i == self.car_color_index:
                pygame.draw.rect(self.screen, YELLOW, color_rect, 3, border_radius=5)
        
        self.save_button.draw(self.screen, self.font)
        self.back_button.draw(self.screen, self.font)


class GameOverScreen:
    """Game over screen with stats"""
    
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont("Arial", 48, bold=True)
        self.font = pygame.font.SysFont("Arial", 24)
        self.font_small = pygame.font.SysFont("Arial", 16)
        
        self.score = 0
        self.distance = 0
        self.coins = 0
        
        button_width = 100
        self.buttons = {
            'retry': Button(SCREEN_WIDTH // 2 - button_width - 10, 500, button_width, 40, "RETRY", GREEN),
            'menu': Button(SCREEN_WIDTH // 2 + 10, 500, button_width, 40, "MENU", BLUE),
        }
    
    def set_stats(self, score, distance, coins):
        self.score = score
        self.distance = distance
        self.coins = coins
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True
        
        for key, button in self.buttons.items():
            button.update(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_click):
                return key
        
        return None
    
    def draw(self):
        self.screen.fill(DARK)
        
        title = self.font_title.render("GAME OVER", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        stats = [
            (f"Final Score: {self.score}", 180),
            (f"Distance: {int(self.distance)}m", 230),
            (f"Coins Collected: {self.coins}", 280),
        ]
        
        for text, y in stats:
            stat_text = self.font.render(text, True, WHITE)
            stat_rect = stat_text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(stat_text, stat_rect)
        
        for button in self.buttons.values():
            button.draw(self.screen, self.font)