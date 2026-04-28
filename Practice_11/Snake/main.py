import pygame
import sys

from snake import (
    Snake, Food,
    draw_field, draw_hud, end_screen,
    screen, clock,
    BASE_FPS, BASE_MOVE, FOOD_PER_LEVEL,
)


def main():
    snake = Snake()
    food  = Food()
    food.respawn(snake.body)

    score       = 0
    level       = 1
    food_eaten  = 0
    move_delay  = BASE_MOVE
    frame_count = 0

    while True:
        # dt_ms — реальное время кадра в миллисекундах (нужно для таймера)
        dt_ms = clock.tick(BASE_FPS)
        frame_count += 1

        # ── Ввод ─────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP,    pygame.K_w): snake.set_direction( 0, -1)
                if event.key in (pygame.K_DOWN,  pygame.K_s): snake.set_direction( 0,  1)
                if event.key in (pygame.K_LEFT,  pygame.K_a): snake.set_direction(-1,  0)
                if event.key in (pygame.K_RIGHT, pygame.K_d): snake.set_direction( 1,  0)
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        # ── Таймер фрукта: обновляем каждый кадр ────────────────
        # food.update() возвращает True когда 6 секунд прошло
        expired = food.update(dt_ms)
        if expired:
            # Фрукт исчез — спавним новый
            food.respawn(snake.body)

        # ── Движение змейки ──────────────────────────────────────
        if frame_count % move_delay == 0:
            alive = snake.step()

            if not alive:
                draw_field(screen)
                food.draw(screen)
                snake.draw(screen)
                draw_hud(screen, score, level)
                pygame.display.flip()
                if end_screen(score, level):
                    main()
                return

            # ── Съел фрукт? ──────────────────────────────────────
            if snake.body[0] == food.pos:
                pts = food.points        # берём очки ЭТОГО фрукта (+1/+3/+5/+10)
                snake.grow()
                score      += pts        # прибавляем реальные очки фрукта
                food_eaten += 1
                food.respawn(snake.body) # новый фрукт с новым таймером

                # Левел-ап
                if food_eaten >= FOOD_PER_LEVEL:
                    level      += 1
                    food_eaten  = 0
                    move_delay  = max(2, move_delay - 1)

        # ── Отрисовка ────────────────────────────────────────────
        draw_field(screen)
        food.draw(screen)   # рисует фрукт + ползунок таймера под ним
        snake.draw(screen)
        draw_hud(screen, score, level)
        pygame.display.flip()


if __name__ == "__main__":
    main()
