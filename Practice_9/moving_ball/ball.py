import pygame


class Ball:
    def __init__(self, screen_width, screen_height):
        self.radius = 25
        self.x = screen_width // 2
        self.y = screen_height // 2
        self.step = 20
        self.color = (255, 0, 0)
        self.screen_width = screen_width
        self.screen_height = screen_height

    def move(self, direction):
        if direction == "up" and self.y - self.radius - self.step >= 0:
            self.y -= self.step
        elif direction == "down" and self.y + self.radius + self.step <= self.screen_height:
            self.y += self.step
        elif direction == "left" and self.x - self.radius - self.step >= 0:
            self.x -= self.step
        elif direction == "right" and self.x + self.radius + self.step <= self.screen_width:
            self.x += self.step

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)
