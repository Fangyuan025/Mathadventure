import pygame
import math
import random


class AttackEffect:
    def __init__(self, start_pos, target_pos, image, speed=10, scale_factor=1.0, rotation=True, trail=False):
        # Basic properties
        self.original_image = image
        self.image = pygame.transform.scale(image,
                                            (int(image.get_width() * scale_factor),
                                             int(image.get_height() * scale_factor)))
        self.pos = list(start_pos)
        self.target = list(target_pos)
        self.speed = speed
        self.active = True

        # Enhanced visual properties
        self.rotation = rotation
        self.angle = 0
        self.trail = trail
        self.trail_positions = []
        self.max_trail_length = 10

        # Explosion properties
        self.exploding = False
        self.explosion_frames = []
        self.explosion_frame_index = 0
        self.explosion_speed = 2  # Frames per update
        self.explosion_counter = 0
        self.explosion_scale = 1.0
        self.explosion_grow_factor = 1.2  # How much the explosion grows
        self.explosion_rotation = 0
        self.explosion_rotation_speed = random.uniform(-2, 2)  # Random rotation
        self.explosion_alpha = 255
        self.explosion_flash = True
        self.flash_intensity = 255
        self.flash_duration = 5
        self.flash_color = (255, 255, 255)  # Default flash color (white)

        # Calculate initial direction for proper orientation
        dx = self.target[0] - self.pos[0]
        dy = self.target[1] - self.pos[1]
        self.angle = math.degrees(math.atan2(-dy, dx))

        # Particle effects
        self.particles = []

    def create_explosion_frames(self, explosion_sheet, frame_width, frame_height, num_frames, num_rows=1):
        """Set up explosion animation from a spritesheet

        Args:
            explosion_sheet: The spritesheet image containing all frames
            frame_width: Width of each frame in pixels
            frame_height: Height of each frame in pixels
            num_frames: Total number of frames to extract
            num_rows: Number of rows in the spritesheet (default: 1, for horizontal strip)
        """
        frames_per_row = num_frames // num_rows if num_rows > 0 else num_frames

        for row in range(num_rows):
            for col in range(frames_per_row):
                frame_idx = row * frames_per_row + col
                if frame_idx >= num_frames:
                    break

                # Extract the frame from the spritesheet
                frame = explosion_sheet.subsurface(
                    (col * frame_width, row * frame_height, frame_width, frame_height)
                )
                self.explosion_frames.append(frame)

    def set_explosion_properties(self, scale=1.0, grow_factor=1.2, rotation=True,
                                 flash=True, flash_color=(255, 255, 255),
                                 flash_intensity=255, flash_duration=5):
        """Configure explosion properties for more control

        Args:
            scale: Base scale of the explosion (default: 1.0)
            grow_factor: How much the explosion grows during animation (default: 1.2)
            rotation: Whether to rotate the explosion (default: True)
            flash: Whether to create a flash effect (default: True)
            flash_color: RGB color of the flash (default: white)
            flash_intensity: Brightness of the flash (0-255)
            flash_duration: How many frames the flash lasts
        """
        self.explosion_scale = scale
        self.explosion_grow_factor = grow_factor
        self.explosion_rotation = random.uniform(0, 360) if rotation else 0
        self.explosion_rotation_speed = random.uniform(-3, 3) if rotation else 0
        self.explosion_flash = flash
        self.flash_color = flash_color
        self.flash_intensity = flash_intensity
        self.flash_duration = flash_duration

    def update(self):
        if not self.active:
            return

        if self.exploding:
            # Update explosion animation
            self.explosion_counter += 1

            # Update flash effect at the beginning of explosion
            if self.explosion_flash and self.explosion_frame_index == 0:
                self.flash_intensity = max(0, self.flash_intensity - (255 / self.flash_duration))

            # Progress to next frame
            if self.explosion_counter >= self.explosion_speed:
                self.explosion_counter = 0
                self.explosion_frame_index += 1

                # Gradually grow the explosion
                self.explosion_scale *= self.explosion_grow_factor

                # Rotate the explosion
                self.explosion_rotation += self.explosion_rotation_speed

                # Create more particles during explosion phases
                particle_count = 5 if self.explosion_frame_index < len(self.explosion_frames) // 2 else 2
                if len(self.particles) < 30:
                    for _ in range(particle_count):
                        # Create larger particles at start, smaller as explosion continues
                        size_range = (4, 8) if self.explosion_frame_index < 2 else (2, 5)
                        life_range = (30, 50) if self.explosion_frame_index < 2 else (15, 30)
                        self._add_particle(size_range=size_range, life_range=life_range,
                                           speed_range=(1, 4), use_physics=True)

                # Fade out the explosion near the end
                if self.explosion_frame_index > len(self.explosion_frames) * 0.7:
                    self.explosion_alpha = max(0, self.explosion_alpha - 25)

                # End the explosion when frames are exhausted
                if self.explosion_frame_index >= len(self.explosion_frames):
                    self.active = False

            # Update any active particles
            self._update_particles()
            return

        # Movement logic
        dx = self.target[0] - self.pos[0]
        dy = self.target[1] - self.pos[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # Store trail position before moving
        if self.trail and len(self.trail_positions) < self.max_trail_length:
            self.trail_positions.append(list(self.pos))
        elif self.trail:
            self.trail_positions.pop(0)
            self.trail_positions.append(list(self.pos))

        # Update position
        if distance < self.speed:
            self.pos = self.target
            self.exploding = True
            # Add initial particles when explosion starts
            for _ in range(10):
                self._add_particle()
        else:
            # Update angle for rotation
            if self.rotation:
                self.angle = math.degrees(math.atan2(-dy, dx))

            # Movement
            self.pos[0] += self.speed * dx / distance
            self.pos[1] += self.speed * dy / distance

            # Occasionally add particles during flight
            if random.random() < 0.3 and self.trail:
                self._add_particle(size_range=(1, 3), life_range=(5, 15), speed_range=(0.5, 1.5))

        # Update any active particles
        self._update_particles()

    def _add_particle(self, size_range=(2, 5), life_range=(20, 40), speed_range=(1, 3), use_physics=False):
        """Add a particle effect with optional physics

        Args:
            size_range: Min and max particle size (default: (2, 5))
            life_range: Min and max particle lifetime in frames (default: (20, 40))
            speed_range: Min and max particle speed (default: (1, 3))
            use_physics: Whether to apply gravity and other physics (default: False)
        """
        size = random.randint(size_range[0], size_range[1])
        life = random.randint(life_range[0], life_range[1])

        # Random direction
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(speed_range[0], speed_range[1])
        velocity = [math.cos(angle) * speed, math.sin(angle) * speed]

        # Random color based on explosion stage
        if self.explosion_frame_index < 2:  # Early explosion
            color = random.choice([
                (255, 255, 255),  # White (center core)
                (255, 255, 180),  # Bright yellow
                (255, 220, 150),  # Bright orange
            ])
        else:  # Later explosion
            color = random.choice([
                (255, 255, 0),  # Yellow
                (255, 165, 0),  # Orange
                (255, 69, 0),  # Red-Orange
                (255, 0, 0),  # Red
                (100, 100, 100),  # Smoke gray
            ])

        # Randomize starting position slightly
        pos_variance = 5 if self.exploding else 2
        start_pos = [
            self.pos[0] + random.uniform(-pos_variance, pos_variance),
            self.pos[1] + random.uniform(-pos_variance, pos_variance)
        ]

        particle = {
            'pos': start_pos,
            'velocity': velocity,
            'size': size,
            'color': color,
            'life': life,
            'max_life': life,  # Store original life for fading
            'use_physics': use_physics,
            'gravity': 0.1 if use_physics else 0,
            'drag': 0.98 if use_physics else 1.0,
            'rotation': random.uniform(0, 360),
            'rotation_speed': random.uniform(-5, 5)
        }

        self.particles.append(particle)

    def _update_particles(self):
        """Update all particles with physics and effects"""
        for particle in self.particles[:]:
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
                continue

            # Apply physics if enabled
            if particle['use_physics']:
                # Apply gravity
                particle['velocity'][1] += particle['gravity']

                # Apply drag (air resistance)
                particle['velocity'][0] *= particle['drag']
                particle['velocity'][1] *= particle['drag']

                # Update rotation
                particle['rotation'] += particle['rotation_speed']

            # Update position
            particle['pos'][0] += particle['velocity'][0]
            particle['pos'][1] += particle['velocity'][1]

            # Calculate fade based on remaining life
            life_ratio = particle['life'] / particle['max_life']

            # Fade out by reducing size
            if life_ratio < 0.5:
                particle['size'] = max(1, particle['size'] * 0.95)

            # Fade out color for smoke particles (gray ones)
            if particle['color'][0] == particle['color'][1] == particle['color'][2] and particle['color'][0] < 200:
                # For smoke/gray particles, increase transparency as they age
                alpha_factor = min(1.0, life_ratio * 1.5)  # Fade out slower at first
                particle['alpha'] = int(255 * alpha_factor)
            else:
                particle['alpha'] = 255

    def draw(self, screen):
        if not self.active:
            return

        # Draw trail if enabled
        if self.trail and self.trail_positions:
            for i, pos in enumerate(self.trail_positions):
                # Calculate alpha based on position in trail
                alpha = int(255 * (i / len(self.trail_positions)))
                size_factor = 0.5 + (i / len(self.trail_positions)) * 0.5

                # Create a smaller, faded copy of the projectile image
                trail_image = pygame.transform.scale(
                    self.original_image,
                    (int(self.image.get_width() * size_factor),
                     int(self.image.get_height() * size_factor))
                )

                # Create a surface with per-pixel alpha
                trail_surface = pygame.Surface(trail_image.get_size(), pygame.SRCALPHA)
                trail_surface.fill((255, 255, 255, alpha))

                # Blit with blend mode
                trail_image.set_alpha(alpha)
                screen.blit(trail_image, pos)

        # Draw particles
        for particle in self.particles:
            # For normal particles, draw circles
            if not hasattr(particle, 'rotation'):
                # Get alpha value if it exists, otherwise use 255
                alpha = particle.get('alpha', 255)

                if alpha < 255:
                    # Create a surface with per-pixel alpha for fading particles
                    particle_surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                    pygame.draw.circle(
                        particle_surf,
                        particle['color'] + (alpha,),  # Add alpha to color tuple
                        (particle['size'], particle['size']),
                        particle['size']
                    )
                    screen.blit(particle_surf,
                                (int(particle['pos'][0] - particle['size']),
                                 int(particle['pos'][1] - particle['size'])))
                else:
                    # Regular particles with full opacity
                    pygame.draw.circle(
                        screen,
                        particle['color'],
                        (int(particle['pos'][0]), int(particle['pos'][1])),
                        particle['size']
                    )
            else:
                # For rotating particles (debris/embers), draw rectangles or squares
                if random.random() < 0.3:  # Only some particles are rotating shapes
                    size = particle['size']
                    particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)

                    # Draw a shape on the surface
                    shape_type = particle.get('shape_type', random.choice(['rect', 'triangle']))
                    if shape_type == 'rect':
                        pygame.draw.rect(
                            particle_surf,
                            particle['color'] + (particle.get('alpha', 255),),
                            (size // 2, size // 2, size, size)
                        )
                    elif shape_type == 'triangle':
                        pygame.draw.polygon(
                            particle_surf,
                            particle['color'] + (particle.get('alpha', 255),),
                            [(size // 2, 0), (0, size * 2), (size * 2, size * 2)]
                        )

                    # Rotate the surface
                    rotated = pygame.transform.rotate(particle_surf, particle['rotation'])
                    rot_rect = rotated.get_rect(center=(int(particle['pos'][0]), int(particle['pos'][1])))
                    screen.blit(rotated, rot_rect)
                else:
                    # Regular circular particles
                    pygame.draw.circle(
                        screen,
                        particle['color'],
                        (int(particle['pos'][0]), int(particle['pos'][1])),
                        particle['size']
                    )

        # Draw the main projectile or explosion
        if self.exploding:
            # Draw flash effect at the beginning of explosion
            if self.explosion_flash and self.flash_intensity > 0:
                # Create a surface for the flash with alpha
                flash_size = 100  # Size of flash
                flash_surf = pygame.Surface((flash_size * 2, flash_size * 2), pygame.SRCALPHA)

                # Create a radial gradient for the flash
                for radius in range(flash_size, 0, -10):
                    alpha = int(self.flash_intensity * (radius / flash_size))
                    pygame.draw.circle(
                        flash_surf,
                        self.flash_color + (alpha,),
                        (flash_size, flash_size),
                        radius
                    )

                # Blit the flash
                flash_rect = flash_surf.get_rect(center=(self.pos[0], self.pos[1]))
                screen.blit(flash_surf, flash_rect)

            # Draw current explosion frame if available
            if self.explosion_frames and self.explosion_frame_index < len(self.explosion_frames):
                explosion_img = self.explosion_frames[self.explosion_frame_index]

                # Apply scaling to make explosion grow or shrink
                scaled_size = (
                    int(explosion_img.get_width() * self.explosion_scale),
                    int(explosion_img.get_height() * self.explosion_scale)
                )
                scaled_img = pygame.transform.scale(explosion_img, scaled_size)

                # Apply rotation if needed
                if self.explosion_rotation_speed != 0:
                    scaled_img = pygame.transform.rotate(scaled_img, self.explosion_rotation)

                # Apply fade out if needed
                if self.explosion_alpha < 255:
                    scaled_img.set_alpha(self.explosion_alpha)

                # Draw the explosion
                explosion_rect = scaled_img.get_rect(center=(self.pos[0], self.pos[1]))
                screen.blit(scaled_img, explosion_rect)

                # Add a glow effect for more intense explosions
                if self.explosion_frame_index < len(self.explosion_frames) // 2:
                    glow_surf = pygame.Surface((scaled_size[0] + 20, scaled_size[1] + 20), pygame.SRCALPHA)
                    glow_color = (255, 200, 100, 100)  # Orange glow with alpha
                    glow_radius = max(scaled_size) // 2 + 10
                    pygame.draw.circle(
                        glow_surf,
                        glow_color,
                        (glow_surf.get_width() // 2, glow_surf.get_height() // 2),
                        glow_radius
                    )
                    glow_rect = glow_surf.get_rect(center=(self.pos[0], self.pos[1]))
                    screen.blit(glow_surf, glow_rect, special_flags=pygame.BLEND_ADD)
        else:
            # Draw the projectile with rotation if enabled
            if self.rotation:
                rotated_image = pygame.transform.rotate(self.image, self.angle)
                rect = rotated_image.get_rect(center=(self.pos[0], self.pos[1]))
                screen.blit(rotated_image, rect)
            else:
                rect = self.image.get_rect(center=(self.pos[0], self.pos[1]))
                screen.blit(self.image, rect)


