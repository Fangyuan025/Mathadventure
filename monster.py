# monster.py
import pygame
from constants import *

class Monster:
    def __init__(self, hp, level, x, y, is_boss=False):
        self.hp = hp
        self.max_hp = hp
        self.level = level
        self.x = x
        self.y = y
        self.is_boss = is_boss
        self.hit_flash_timer = 0  # ⬅ 闪烁帧数

        # 加载图像（你可以根据实际路径修改）
        if is_boss:
            raw_image = pygame.image.load("assets/boss_monster.png")
            self.image = pygame.transform.scale(raw_image, (200, 200))  # 放大Boss
            self.width = 200
            self.height = 200
        else:
            raw_image = pygame.image.load("assets/normal_monster.png")
            self.image = pygame.transform.scale(raw_image, (150, 150))  # 放大普通怪
            self.width = 150
            self.height = 150

        self.x = min(max(self.x, 10), WIDTH - self.width - 10)
        self.y = min(max(self.y, 10), HEIGHT - self.height - 10)

    def draw(self, screen):
        if self.hit_flash_timer > 0:
            # 显示被击中特效颜色
            flash_image = self.image.copy()
            flash_image.fill((255, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
            screen.blit(flash_image, (self.x, self.y))
            self.hit_flash_timer -= 1
        else:
            screen.blit(self.image, (self.x, self.y))

        bar_x = self.x
        bar_y = self.y - 50  # 上移到图片上方

        hp_ratio = self.hp / self.max_hp
        hp_bar_width = self.width * hp_ratio

        # 背景条
        pygame.draw.rect(screen, RED, (bar_x, bar_y, self.width, 6))
        # 当前HP
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, hp_bar_width, 6))

