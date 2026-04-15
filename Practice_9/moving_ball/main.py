import pygame
import sys
from ball import Ball

WIDTH, HEIGHT = 600, 600
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball")
clock = pygame.time.Clock()

ball = Ball(WIDTH, HEIGHT)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                ball.move("up")
            elif event.key == pygame.K_DOWN:
                ball.move("down")
            elif event.key == pygame.K_LEFT:
                ball.move("left")
            elif event.key == pygame.K_RIGHT:
                ball.move("right")

    screen.fill((255, 255, 255))
    ball.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
