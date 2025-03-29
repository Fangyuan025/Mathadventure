# utils.py
import pygame
import numpy as np
from constants import *


def draw_text(screen, text, color, x, y):
    text_surface = FONT.render(text, True, color)
    screen.blit(text_surface, (x, y))


def generate_sound(frequency, duration):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    sound_array = np.c_[wave, wave].astype(np.float32)
    sound = pygame.sndarray.make_sound((sound_array * 32767).astype(np.int16))
    return sound
