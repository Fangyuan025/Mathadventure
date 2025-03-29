# monster.py
from constants import *

class Monster:
    def __init__(self, hp, level, x, y, is_boss=False):
        self.hp = hp
        self.max_hp = hp
        self.level = level
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.is_boss = is_boss
        self.color = YELLOW if is_boss else RED
        # Scale boss size
        if is_boss:
            self.width = 70
            self.height = 70

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        hp_bar_width = self.width * (self.hp / self.max_hp)
        pygame.draw.rect(screen, RED, (self.x, self.y - 10, self.width, 5))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, hp_bar_width, 5))