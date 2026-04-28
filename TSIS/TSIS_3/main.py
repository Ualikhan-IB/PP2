"""
Racer Game - TSIS3 Complete Edition
Fixed: Movement, Leaderboard saving, All features working
"""

import pygame
import sys
from racer import Game
from ui import (
    MainMenu, LeaderboardScreen, SettingsScreen,
    GameOverScreen, UsernamePrompt
)
from persistence import load_settings, save_settings, load_leaderboard, save_score

pygame.init()
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600


def main():
    """Main game loop with screen management"""
    # Create main screen ONCE
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Racer Game - TSIS3")
    clock = pygame.time.Clock()
    
    settings = load_settings()
    
    # Initialize screens with screen reference
    main_menu = MainMenu(screen)
    leaderboard_screen = LeaderboardScreen(screen)
    settings_screen = SettingsScreen(screen, settings)
    username_prompt = UsernamePrompt(screen)
    game_over_screen_obj = GameOverScreen(screen)
    
    current_screen = "menu"
    game = None
    username = None
    
    running = True
    
    while running:
        dt = clock.tick(60)
        
        if current_screen == "menu":
            action = main_menu.handle_events()
            main_menu.draw()
            
            if action == "play":
                current_screen = "username"
            elif action == "leaderboard":
                leaderboard_screen.refresh()
                current_screen = "leaderboard"
            elif action == "settings":
                settings_screen.refresh()
                current_screen = "settings"
            elif action == "quit":
                running = False
        
        elif current_screen == "username":
            username, action = username_prompt.handle_events()
            username_prompt.draw()
            
            if action == "play" and username:
                game = Game(screen, username, settings)
                current_screen = "game"
            elif action == "back":
                current_screen = "menu"
        
        elif current_screen == "game":
            if game.running:
                game.handle_events()
                game.update(dt)
                game.draw()
            else:
                # Game over - show results and save to leaderboard
                game_over_screen_obj.set_stats(game.score, game.distance, game.total_coins)
                # Save to leaderboard
                save_score(username, game.score, game.distance, game.total_coins)
                current_screen = "game_over"
        
        elif current_screen == "game_over":
            action = game_over_screen_obj.handle_events()
            game_over_screen_obj.draw()
            
            if action == "retry":
                game = Game(screen, username, settings)
                current_screen = "game"
            elif action == "menu":
                current_screen = "menu"
            elif action == "quit":
                running = False
        
        elif current_screen == "leaderboard":
            action = leaderboard_screen.handle_events()
            leaderboard_screen.draw()
            
            if action == "back":
                current_screen = "menu"
        
        elif current_screen == "settings":
            action, new_settings = settings_screen.handle_events()
            settings_screen.draw()
            
            if action == "save":
                save_settings(new_settings)
                settings = new_settings
                current_screen = "menu"
            elif action == "back":
                current_screen = "menu"
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()