import pygame
import random
import sys

from racer import (
    PlayerCar, EnemyCar, Coin,
    draw_road, draw_hud, draw_coin_legend, game_over_screen,
    screen, clock,
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    SPEED_UP_EVERY, ENEMY_BASE_SPEED, ENEMY_SPEED_STEP, ENEMY_SPEED_MAX
)


def main():
    """Main game loop with weighted coins and dynamic enemy speed."""
    player = PlayerCar()
    enemies = []
    coins = []
    
    # Game state
    score = 0                    # Frames survived
    total_coin_value = 0         # Sum of all coin values collected (Task 2)
    road_offset = 0
    
    # Task 2: Enemy speed increases based on total coin VALUE
    enemy_speed = float(ENEMY_BASE_SPEED)
    
    # Spawn timers (frames instead of milliseconds for better control)
    enemy_timer = 0
    coin_timer = 0
    ENEMY_INTERVAL = 90   # ~1.5 seconds at 60 FPS
    COIN_INTERVAL = 45    # ~0.75 seconds at 60 FPS
    
    running = True
    
    while running:
        dt = clock.tick(FPS)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # Player movement
        keys = pygame.key.get_pressed()
        player.move(keys)
        
        # ── Task 2: Update enemy speed based on total coin VALUE ──
        # Each coin adds its value (1, 3, 5, or 10) to total_coin_value
        # Every SPEED_UP_EVERY points, enemy speed increases
        speed_level = total_coin_value // SPEED_UP_EVERY
        enemy_speed = min(
            ENEMY_BASE_SPEED + speed_level * ENEMY_SPEED_STEP,
            ENEMY_SPEED_MAX
        )
        coins_into_level = total_coin_value % SPEED_UP_EVERY
        
        # Spawn enemies using frame timer
        enemy_timer += 1
        if enemy_timer >= ENEMY_INTERVAL:
            enemy_timer = 0
            enemies.append(EnemyCar(enemy_speed))
        
        # Spawn coins using frame timer
        coin_timer += 1
        if coin_timer >= COIN_INTERVAL:
            coin_timer = 0
            # Pass current enemies to avoid spawning inside cars
            coins.append(Coin(enemies))
        
        # Update enemies
        for e in enemies[:]:
            e.update()
            e.speed = enemy_speed  # Sync speed for existing enemies
            if e.is_off_screen():
                enemies.remove(e)
                score += 1  # Score increases when enemy passes safely
        
        # Update coins
        for c in coins[:]:
            c.update()
            if c.is_off_screen():
                coins.remove(c)
        
        # Collision: player vs enemy → game over
        for e in enemies:
            if player.rect.colliderect(e.rect):
                if game_over_screen(score, total_coin_value):
                    main()  # Restart
                return
        
        # Collision: player vs coin → collect with weighted value
        for c in coins[:]:
            if player.rect.colliderect(c.rect):
                coins.remove(c)
                total_coin_value += c.value  # Task 1: Add coin's VALUE (1,3,5,10)
                # Optional: Add score bonus for collecting coins
                score += c.value
        
        # Update scrolling road
        road_offset = (road_offset + int(enemy_speed)) % 80
        
        # Draw everything
        draw_road(screen, road_offset)
        
        for e in enemies:
            e.draw(screen)
        for c in coins:
            c.draw(screen)
        player.draw(screen)
        
        # Draw HUD with speed and progress bar
        draw_hud(screen, score, total_coin_value, enemy_speed, coins_into_level)
        
        # Draw coin type legend
        draw_coin_legend(screen)
        
        pygame.display.flip()


if __name__ == "__main__":
    main()