# player.py
from constants import *


class Player:
    def __init__(self):
        self.hp = 5
        self.max_hp = 5
        self.x = 100
        self.y = 500
        self.width = 50
        self.height = 50
        self.speed = 5
        self.coins = 0
        self.score = 0  # Added score
        self.color = GREEN

    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        elif direction == "right" and self.x < WIDTH - self.width:
            self.x += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        hp_bar_width = self.width * (self.hp / self.max_hp)
        pygame.draw.rect(screen, RED, (self.x, self.y - 10, self.width, 5))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, hp_bar_width, 5))
