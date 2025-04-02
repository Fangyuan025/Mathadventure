# player.py
import pygame
from constants import *

class Player:
    def __init__(self):
        self.hp = 5
        self.max_hp = 5
        self.level = 1
        self.x = 100
        self.y = 500
        self.speed = 5
        self.coins = 0
        self.score = 0

        raw_image = pygame.image.load("assets/player_icon.png")
        self.width = 150
        self.height = 150
        self.image = pygame.transform.scale(raw_image, (self.width, self.height))

        self.x = min(max(self.x, 10), WIDTH - self.width - 10)
        self.y = min(max(self.y, 10), HEIGHT - self.height - 10)

    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        elif direction == "right" and self.x < WIDTH - self.width:
            self.x += self.speed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

        bar_x = self.x
        bar_y = self.y - 30
        hp_ratio = self.hp / self.max_hp
        hp_bar_width = self.width * hp_ratio

        pygame.draw.rect(screen, RED, (bar_x, bar_y, self.width, 6))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, hp_bar_width, 6))

