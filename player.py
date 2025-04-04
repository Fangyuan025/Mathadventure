# player.py
import pygame
import random
import math
from constants import *


class Player:
    def __init__(self):
        self.hp = 5
        self.max_hp = 5
        self.displayed_hp = 5.0  # New floating-point variable for animated HP
        self.level = 1
        self.x = 100
        self.y = 500
        self.speed = 5
        self.coins = 0
        self.score = 0

        # Add shake effect variables
        self.shake_duration = 0
        self.shake_intensity = 8  # Maximum shake offset in pixels
        self.original_x = self.x
        self.original_y = self.y
        self.hit_flash_timer = 0  # For flash effect when hit

        # Breathing animation variables
        self.breath_scale = 1.0
        self.breath_direction = 1  # 1 for inhale (growing), -1 for exhale (shrinking)
        self.breath_speed = 0.001
        self.breath_min = 0.98
        self.breath_max = 1.02

        # Show-up animation variables
        self.show_up_scale = 0.1  # Start very small
        self.show_up_duration = 45  # frames for show-up animation (0.75 second at 60fps)
        self.show_up_timer = self.show_up_duration
        self.is_showing_up = True

        # HP animation variables
        self.is_hp_animating = False
        self.hp_animation_speed = 0.05  # How quickly HP decreases
        self.hp_pulse_timer = 0
        self.hp_pulse_duration = 30

        # Load image
        raw_image = pygame.image.load("assets/player_icon.png")
        self.width = 150
        self.height = 150
        self.image = pygame.transform.scale(raw_image, (self.width, self.height))

        # Store the original image and dimensions
        self.original_image = self.image
        self.original_width = self.width
        self.original_height = self.height

        self.x = min(max(self.x, 10), WIDTH - self.width - 10)
        self.y = min(max(self.y, 10), HEIGHT - self.height - 10)
        self.original_x = self.x
        self.original_y = self.y

    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
            self.original_x = self.x  # Update original position for shake effect
        elif direction == "right" and self.x < WIDTH - self.width:
            self.x += self.speed
            self.original_x = self.x  # Update original position for shake effect

    def take_hit(self):
        """Called when player is hit"""
        self.hit_flash_timer = 8
        self.shake_duration = 15
        self.is_hp_animating = True
        self.hp_pulse_timer = self.hp_pulse_duration

    def update(self):
        """Update player state each frame"""
        # Update HP animation
        if self.is_hp_animating:
            # Animate HP going down
            if self.displayed_hp > self.hp:
                self.displayed_hp -= self.hp_animation_speed
                if self.displayed_hp <= self.hp:
                    self.displayed_hp = float(self.hp)
                    self.is_hp_animating = False

            # Pulse the health bar when taking damage
            if self.hp_pulse_timer > 0:
                self.hp_pulse_timer -= 1

        if self.is_showing_up:
            # Handle show-up animation
            if self.show_up_timer > 0:
                progress = 1 - (self.show_up_timer / self.show_up_duration)
                self.show_up_scale = 0.1 + progress * 0.9  # Grows from 0.1 to 1.0

                # Add heroic entry effect - slightly overshoot then settle
                if progress > 0.7:
                    overshoot = math.sin((progress - 0.7) * 5 * math.pi) * 0.06
                    self.show_up_scale = min(1.0 + overshoot, 1.06)

                self.show_up_timer -= 1
            else:
                self.is_showing_up = False
        else:
            # Apply breathing effect only when not showing up
            self.breath_scale += self.breath_speed * self.breath_direction

            # Change breathing direction when limits are reached
            if self.breath_scale >= self.breath_max:
                self.breath_direction = -1
            elif self.breath_scale <= self.breath_min:
                self.breath_direction = 1

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1

        # Handle shake effect
        if self.shake_duration > 0:
            # Generate random offset for shaking
            offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            offset_y = random.randint(-self.shake_intensity, self.shake_intensity)

            # Apply offset to position
            self.x = self.original_x + offset_x
            self.y = self.original_y + offset_y

            # Reduce shake duration
            self.shake_duration -= 1

            # Scale down shake intensity for more realistic effect
            if self.shake_duration < 8:
                self.shake_intensity = 4

            # Reset position when shake is done
            if self.shake_duration <= 0:
                self.x = self.original_x
                self.y = self.original_y
                self.shake_intensity = 8  # Reset intensity for next hit

        # Update current image dimensions based on animations
        if self.is_showing_up:
            scale_factor = self.show_up_scale
        else:
            scale_factor = self.breath_scale

        # Apply scale to the original image
        scaled_width = int(self.original_width * scale_factor)
        scaled_height = int(self.original_height * scale_factor)
        self.image = pygame.transform.scale(self.original_image, (scaled_width, scaled_height))

        # Update width and height for drawing
        self.width = scaled_width
        self.height = scaled_height

    def draw(self, screen):
        # Get the center position for consistent scaling
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2

        # Adjust position to keep the player centered when scaling
        draw_x = center_x - self.image.get_width() / 2
        draw_y = center_y - self.image.get_height() / 2

        if self.hit_flash_timer > 0:
            # Flash effect when hit
            flash_image = self.image.copy()
            flash_image.fill((255, 100, 100), special_flags=pygame.BLEND_RGB_ADD)
            screen.blit(flash_image, (draw_x, draw_y))
        else:
            screen.blit(self.image, (draw_x, draw_y))

        # Health bar position - adjust based on current size
        bar_x = draw_x
        bar_y = draw_y - 30
        bar_width = self.image.get_width()

        # Calculate the ratio for displayed HP (for animation)
        displayed_hp_ratio = self.displayed_hp / self.max_hp
        hp_bar_width = bar_width * displayed_hp_ratio

        # Draw background HP bar
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, 6))

        # Determine health bar color based on state
        if self.hp_pulse_timer > 0:
            # Pulse between white and green during damage animation
            pulse_intensity = abs(math.sin(self.hp_pulse_timer * 0.4)) * 0.7
            hp_color = (
                int(100 + 155 * pulse_intensity),  # R: Increase for pulsing
                int(200),  # G: Green base
                int(100 * pulse_intensity)  # B: Some blue for lighter green
            )
        else:
            # Normal health color
            hp_color = GREEN

        # Draw current HP with animation
        pygame.draw.rect(screen, hp_color, (bar_x, bar_y, hp_bar_width, 6))

        # Draw tick marks for the health points
        if self.max_hp <= 10:  # Only show ticks for reasonable HP amounts
            for i in range(1, self.max_hp):
                tick_x = bar_x + (bar_width * i / self.max_hp)
                pygame.draw.line(screen, (0, 0, 0, 128),
                                 (tick_x, bar_y),
                                 (tick_x, bar_y + 6),
                                 1)