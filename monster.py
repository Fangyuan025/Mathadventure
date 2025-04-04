import pygame
import random
import math
from constants import *


class Monster:
    def __init__(self, hp, level, x, y, is_boss=False):
        self.hp = hp
        self.max_hp = hp
        self.displayed_hp = float(hp)  # For HP animation
        self.level = level
        self.x = x
        self.y = y
        self.is_boss = is_boss
        self.hit_flash_timer = 0

        # VERY IMPORTANT: Boss HP tracking
        self.boss_hp_debug = hp if is_boss else 0

        # Add shake effect variables
        self.shake_duration = 0
        self.shake_intensity = 10  # Maximum shake offset in pixels
        self.original_x = x
        self.original_y = y

        # Breathing animation variables
        self.breath_scale = 1.0
        self.breath_direction = 1  # 1 for inhale (growing), -1 for exhale (shrinking)
        self.breath_speed = 0.0015 if is_boss else 0.002  # Boss breathes slower
        self.breath_min = 0.97
        self.breath_max = 1.03

        # Show-up animation variables
        self.show_up_scale = 0.1  # Start very small
        self.show_up_duration = 60  # frames for show-up animation (1 second at 60fps)
        self.show_up_timer = self.show_up_duration
        self.is_showing_up = True

        # Death animation variables
        self.is_dying = False
        self.death_timer = 0
        self.death_duration = 90  # frames for death animation (1.5 seconds at 60fps)
        self.death_scale = 1.0
        self.death_alpha = 255
        self.death_rotation = 0
        self.death_y_velocity = 0
        self.death_particles = []

        # Load images
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

        # Store the original image and dimensions
        self.original_image = self.image
        self.original_width = self.width
        self.original_height = self.height

        self.x = min(max(self.x, 10), WIDTH - self.width - 10)
        self.y = min(max(self.y, 10), HEIGHT - self.height - 10)
        self.original_x = self.x
        self.original_y = self.y

    def damage(self, amount=1):
        """Directly reduce HP and handle animations"""
        old_hp = self.hp
        self.hp -= amount

        # Extra safety for bosses
        if self.is_boss:
            self.boss_hp_debug -= amount
            print(f"BOSS DAMAGED: old={old_hp}, new={self.hp}, debug={self.boss_hp_debug}")

        # Set displayed_hp for animation
        self.displayed_hp = float(old_hp)

        # Visual effects
        self.hit_flash_timer = 10
        self.shake_duration = 20

        return self.hp <= 0  # Return True if monster is defeated

    def set_hp(self, new_hp):
        """Set HP to a specific value"""
        old_hp = self.hp
        self.hp = new_hp

        # Extra safety for bosses
        if self.is_boss:
            self.boss_hp_debug = new_hp
            print(f"BOSS SET_HP: old={old_hp}, new={new_hp}, debug={self.boss_hp_debug}")

        # Only animate if HP decreased
        if new_hp < old_hp:
            self.displayed_hp = float(old_hp)
            self.hit_flash_timer = 10
            self.shake_duration = 20
        else:
            # For healing or initialization
            self.displayed_hp = float(new_hp)

        return self.hp <= 0  # Return True if monster is defeated

    def take_hit(self):
        """Visual effects for being hit"""
        self.hit_flash_timer = 10  # Flash for 10 frames
        self.shake_duration = 20  # Shake for 20 frames

    def start_death_animation(self):
        """Begin the death animation sequence"""
        self.is_dying = True
        self.death_timer = self.death_duration
        self.death_y_velocity = -3  # Initial upward velocity for jump effect
        self.death_rotation = random.choice([-1, 1]) * random.uniform(3, 5)  # Random rotation direction

        # Create initial death particles
        self._create_death_particles(20)

    def _create_death_particles(self, count):
        """Create particles for death effect"""
        for _ in range(count):
            # Random position within monster body
            x = self.x + random.uniform(0, self.width)
            y = self.y + random.uniform(0, self.height)

            # Random direction
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 5)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed

            # Random size and lifetime
            size = random.uniform(2, 10)
            lifetime = random.randint(30, 90)

            # Color based on monster type
            if self.is_boss:
                colors = [(255, 50, 50), (200, 0, 0), (150, 0, 0)]  # Red for boss
            else:
                colors = [(100, 255, 100), (0, 200, 0), (0, 150, 0)]  # Green for normal monsters

            color = random.choice(colors)

            # Add particle to list
            self.death_particles.append({
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy,
                'size': size,
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'color': color,
                'gravity': 0.1,
                'type': random.choice(['circle', 'square', 'triangle'])
            })

    def update(self):
        """Update monster state each frame"""
        # Update HP animation
        if self.is_boss:
            # For bosses, force slower animation
            hp_animation_speed = 0.08

            # Special debug check for bosses
            if abs(self.hp - self.boss_hp_debug) > 0.1:
                print(f"WARNING: Boss HP mismatch: hp={self.hp}, debug={self.boss_hp_debug}")
                self.hp = self.boss_hp_debug  # Force correction
        else:
            hp_animation_speed = 0.15

        # Always check for HP animation needs
        if abs(self.displayed_hp - self.hp) > 0.01:
            if self.displayed_hp > self.hp:
                # Print info about boss HP animation
                if self.is_boss:
                    print(f"Boss HP animating: {self.displayed_hp} -> {self.hp}, speed={hp_animation_speed}")

                self.displayed_hp -= hp_animation_speed
                if self.displayed_hp < self.hp:
                    self.displayed_hp = float(self.hp)
            elif self.displayed_hp < self.hp:
                self.displayed_hp += hp_animation_speed
                if self.displayed_hp > self.hp:
                    self.displayed_hp = float(self.hp)

        # Handle death animation
        if self.is_dying:
            self.death_timer -= 1

            # Apply gravity to monster during death animation
            self.death_y_velocity += 0.2  # Gravity
            self.y += self.death_y_velocity

            # Rotate monster
            self.death_rotation *= 0.95  # Slow down rotation over time

            # Fade out and scale down
            progress = 1 - (self.death_timer / self.death_duration)

            if progress < 0.3:
                # Initial phase: grow slightly and start rotating
                self.death_scale = 1.0 + progress * 0.2
                self.death_alpha = 255
            elif progress < 0.7:
                # Middle phase: maintain size but start fading
                self.death_scale = 1.2 - (progress - 0.3) * 0.4
                self.death_alpha = 255 - int((progress - 0.3) * 400)
            else:
                # Final phase: shrink and fade out completely
                self.death_scale = 0.8 - (progress - 0.7) * 0.8
                self.death_alpha = max(0, 153 - int((progress - 0.7) * 510))

            # Update death particles
            for particle in self.death_particles[:]:
                particle['lifetime'] -= 1
                if particle['lifetime'] <= 0:
                    self.death_particles.remove(particle)
                    continue

                # Update position
                particle['x'] += particle['dx']
                particle['dx'] *= 0.95  # Slow down horizontally

                particle['dy'] += particle['gravity']  # Apply gravity
                particle['y'] += particle['dy']

                # Fade based on lifetime
                fade_ratio = particle['lifetime'] / particle['max_lifetime']

                # Shrink particles over time
                if fade_ratio < 0.5:
                    particle['size'] *= 0.95

            # Add more particles occasionally during death animation
            if self.death_timer > 0 and random.random() < 0.2:
                self._create_death_particles(random.randint(1, 3))

            return

        if self.is_showing_up:
            # Handle show-up animation
            if self.show_up_timer > 0:
                progress = 1 - (self.show_up_timer / self.show_up_duration)
                self.show_up_scale = 0.1 + progress * 0.9  # Grows from 0.1 to 1.0

                # Add a little bounce effect at the end
                if progress > 0.8:
                    bounce_factor = math.sin((progress - 0.8) * 5 * math.pi) * 0.05
                    self.show_up_scale = min(1.0 + bounce_factor, 1.05)

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

        # Handle hit flash effect
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
            if self.shake_duration < 10:
                self.shake_intensity = 5

            # Reset position when shake is done
            if self.shake_duration <= 0:
                self.x = self.original_x
                self.y = self.original_y
                self.shake_intensity = 10  # Reset intensity for next hit

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
        if self.is_dying:
            # Get the center position for proper scaling/rotation during death
            center_x = self.x + self.width / 2
            center_y = self.y + self.height / 2

            # Draw death particles first (behind monster)
            for particle in self.death_particles:
                alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))

                if particle['type'] == 'circle':
                    # For fading particles, use a surface with alpha
                    particle_surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                    pygame.draw.circle(
                        particle_surf,
                        particle['color'] + (alpha,),
                        (particle['size'], particle['size']),
                        particle['size']
                    )
                    screen.blit(particle_surf,
                                (int(particle['x'] - particle['size']),
                                 int(particle['y'] - particle['size'])))
                elif particle['type'] == 'square':
                    particle_surf = pygame.Surface((particle['size'], particle['size']), pygame.SRCALPHA)
                    particle_surf.fill(particle['color'] + (alpha,))
                    screen.blit(particle_surf,
                                (int(particle['x'] - particle['size'] / 2),
                                 int(particle['y'] - particle['size'] / 2)))
                elif particle['type'] == 'triangle':
                    particle_surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                    points = [
                        (particle['size'], 0),
                        (0, particle['size'] * 2),
                        (particle['size'] * 2, particle['size'] * 2)
                    ]
                    pygame.draw.polygon(
                        particle_surf,
                        particle['color'] + (alpha,),
                        points
                    )
                    screen.blit(particle_surf,
                                (int(particle['x'] - particle['size']),
                                 int(particle['y'] - particle['size'])))

            # Scale and rotate the monster for death animation
            scaled_size = (
                int(self.original_width * self.death_scale),
                int(self.original_height * self.death_scale)
            )

            if scaled_size[0] > 0 and scaled_size[1] > 0:  # Prevent zero size issues
                # Scale the image
                scaled_image = pygame.transform.scale(self.original_image, scaled_size)

                # Rotate the image
                rotated_image = pygame.transform.rotate(scaled_image, self.death_rotation * self.death_timer)

                # Set transparency
                rotated_image.set_alpha(self.death_alpha)

                # Get the rect for positioning
                image_rect = rotated_image.get_rect(center=(center_x, center_y))

                # Draw the monster
                screen.blit(rotated_image, image_rect)

            return

        # Get the center position for consistent scaling
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2

        # Adjust position to keep the monster centered when scaling
        draw_x = center_x - self.image.get_width() / 2
        draw_y = center_y - self.image.get_height() / 2

        if self.hit_flash_timer > 0:
            # Flash red when hit
            flash_image = self.image.copy()
            flash_image.fill((255, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
            screen.blit(flash_image, (draw_x, draw_y))
        else:
            screen.blit(self.image, (draw_x, draw_y))

        # Don't draw health bar if monster is dying
        if self.is_dying:
            return

        # Health bar position - adjust based on current size
        bar_x = draw_x
        bar_y = draw_y - 30  # Above the monster
        bar_width = self.image.get_width()

        # Calculate the ratio for displayed HP (for animation)
        displayed_hp = max(0, min(self.displayed_hp, self.max_hp))

        # HP Bar width calculation - different for bosses
        if self.is_boss:
            # Special boss calculation - use pixels per HP for more visible changes
            pixels_per_hp = 3  # Each HP point takes up 3 pixels of space
            hp_missing = self.max_hp - displayed_hp
            hp_bar_width = int(bar_width - (hp_missing * pixels_per_hp))
            hp_bar_width = max(0, min(hp_bar_width, bar_width))  # Ensure valid range
        else:
            # Regular monsters use normal percentage
            displayed_hp_ratio = displayed_hp / self.max_hp
            hp_bar_width = max(0, int(bar_width * displayed_hp_ratio))

        # Draw HP bar background
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, 6))

        # Determine health bar color based on state
        if self.hit_flash_timer > 0:
            # Pulse between bright red and regular red during damage animation
            pulse_intensity = abs(math.sin(self.hit_flash_timer * 0.4)) * 0.7
            hp_color = (
                int(200 + 55 * pulse_intensity),  # R: More red for pulsing
                int(100 * pulse_intensity),  # G: Some green for orange-ish flashes
                int(50 * pulse_intensity)  # B: A little blue
            )
        else:
            # Normal health color based on monster type
            if self.is_boss:
                hp_color = (180, 50, 180)  # Darker red for boss
            else:
                hp_color = GREEN

        # Draw current HP bar with animation
        if hp_bar_width > 0:  # Prevent negative width
            pygame.draw.rect(screen, hp_color, (bar_x, bar_y, hp_bar_width, 6))

            # Draw tick marks for boss monsters to indicate phases
            if self.is_boss and self.max_hp > 3:
                marks = 3  # Three phases for boss
                for i in range(1, marks):
                    tick_x = bar_x + (bar_width * i / marks)
                    tick_width = 2 if i == marks // 2 else 1  # Middle mark is thicker
                    pygame.draw.line(screen, (255, 255, 255, 200),
                                     (tick_x, bar_y - 1),
                                     (tick_x, bar_y + 7),
                                     tick_width)

        # Debug HP text for bosses - ONLY DURING DEVELOPMENT
        if self.is_boss:
            debug_font = pygame.font.Font(None, 24)
            debug_text = f"HP: {self.hp}/{self.max_hp} (disp: {self.displayed_hp:.1f})"
            debug_surface = debug_font.render(debug_text, True, (255, 255, 255))
            screen.blit(debug_surface, (bar_x, bar_y - 20))

    def reset_hp_display(self):
        """Reset the displayed HP to match actual HP"""
        self.displayed_hp = float(self.hp)
        if self.is_boss:
            self.boss_hp_debug = self.hp  # Keep debug value in sync